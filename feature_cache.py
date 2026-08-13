import json
import hashlib
from pathlib import Path
from typing import Optional


class FeatureCache:
    """
    Stores previously calculated audio features.

    The cache prevents Musica from analyzing the same
    audio file every time the application starts.
    """

    def __init__(self, cache_file: str = "data/audio_features.json"):
        self.cache_file = Path(cache_file)

        self.cache_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._cache = self._load()

    def _load(self) -> dict:
        """Load existing cache from disk."""

        if not self.cache_file.exists():
            return {}

        try:
            with open(
                self.cache_file,
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self):
        """Save cache to disk."""

        with open(
            self.cache_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self._cache,
                file,
                indent=2,
            )

    def _file_signature(self, file_path: str) -> Optional[str]:
        """
        Create a signature based on the file path,
        modification time and file size.

        If the file changes, its signature changes and
        Musica will analyze it again.
        """

        path = Path(file_path)

        if not path.exists():
            return None

        stat = path.stat()

        raw = (
            f"{path.resolve()}|"
            f"{stat.st_size}|"
            f"{stat.st_mtime_ns}"
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    def get(self, file_path: str) -> Optional[dict]:
        """Return cached features if available."""

        signature = self._file_signature(file_path)

        if signature is None:
            return None

        entry = self._cache.get(signature)

        if entry is None:
            return None

        return entry.get("features")

    def set(
        self,
        file_path: str,
        features: dict,
    ):
        """Store features for a file."""

        signature = self._file_signature(file_path)

        if signature is None:
            return

        self._cache[signature] = {
            "file": str(Path(file_path).resolve()),
            "features": features,
        }

        self._save()