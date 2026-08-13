from pathlib import Path
from typing import List
import hashlib

from core.models import MusicaTrack
from core.metadata import extract_metadata
from core.audio_features import extract_audio_features
from core.feature_cache import FeatureCache


SUPPORTED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
}


class LocalMusicSource:
    """
    Local music source for Musica.

    Responsibilities:
    - Discover local audio files
    - Extract embedded metadata
    - Extract/cache audio features
    - Convert everything into MusicaTrack objects
    """

    def __init__(self, music_directory: str):

        self.music_directory = Path(music_directory)

        self.feature_cache = FeatureCache()

    def _generate_track_id(self, path: Path) -> str:
        """
        Generate a stable ID for a local track.
        """

        raw = str(path.resolve())

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:16]

    def _get_audio_features(self, path: Path) -> dict:
        """
        Get audio features from cache.

        If the track hasn't been analyzed yet,
        analyze it and save the result.
        """

        cached = self.feature_cache.get(str(path))

        if cached is not None:

            print(
                f"[Audio Features] Cache HIT: {path.name}"
            )

            return cached

        print(
            f"[Audio Features] Analyzing: {path.name}"
        )

        features = extract_audio_features(
            str(path)
        )

        if features is None:
            return {}

        self.feature_cache.set(
            str(path),
            features,
        )

        return features

    def scan(
        self,
        limit: int | None = None
    ) -> List[MusicaTrack]:
        """
        Scan the local music directory.

        Args:
            limit:
                Optional maximum number of tracks
                to process.

        Returns:
            List of MusicaTrack objects.
        """

        if not self.music_directory.exists():

            print(
                f"[Local Source] Directory not found: "
                f"{self.music_directory}"
            )

            return []

        tracks = []

        for path in self.music_directory.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            if (
                limit is not None
                and len(tracks) >= limit
            ):
                break

            # -----------------------------------------
            # 1. Generate stable track ID
            # -----------------------------------------

            track_id = self._generate_track_id(path)

            # -----------------------------------------
            # 2. Extract embedded metadata
            # -----------------------------------------

            metadata = extract_metadata(
                str(path)
            )

            # -----------------------------------------
            # 3. Extract/cache audio features
            # -----------------------------------------

            audio_features = self._get_audio_features(
                path
            )

            # -----------------------------------------
            # 4. Get duration
            # -----------------------------------------

            duration = audio_features.get(
                "duration"
            )

            # -----------------------------------------
            # 5. Create common MusicaTrack
            # -----------------------------------------

            track = MusicaTrack(
                id=track_id,

                title=metadata.get(
                    "title",
                    path.stem
                ),

                artist=metadata.get(
                    "artist",
                    "Unknown"
                ),

                album=metadata.get(
                    "album"
                ),

                duration=duration,

                source="local",

                source_id=str(path),

                playback_uri=str(path),

                audio_features=audio_features,

                metadata=metadata,
            )

            tracks.append(track)

        return tracks

    def get_tracks(
        self,
        limit: int | None = None
    ) -> List[MusicaTrack]:
        """
        Public interface for retrieving tracks.

        Currently delegates to scan().
        """

        return self.scan(limit=limit)