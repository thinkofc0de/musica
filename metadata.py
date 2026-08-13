from pathlib import Path
from typing import Optional

from mutagen import File


def extract_metadata(file_path: str) -> dict:
    """
    Extract metadata from an audio file using its embedded tags.

    Returns a normalized dictionary so the rest of Musica
    doesn't need to know which metadata format the file uses.
    """

    path = Path(file_path)

    result = {
        "title": path.stem,
        "artist": "Unknown",
        "album": None,
        "genre": None,
        "year": None,
        "track_number": None,
        "artwork": None,
    }

    try:
        audio = File(path, easy=True)

        if audio is None:
            return result

        result["title"] = _get_first(audio, "title") or path.stem
        result["artist"] = _get_first(audio, "artist") or "Unknown"
        result["album"] = _get_first(audio, "album")
        result["genre"] = _get_first(audio, "genre")
        result["year"] = _get_first(audio, "date")

        track_number = _get_first(audio, "tracknumber")

        if track_number:
            result["track_number"] = track_number

    except Exception as e:
        print(f"[Metadata] Could not read {path.name}: {e}")

    return result


def _get_first(audio, key: str) -> Optional[str]:
    """
    Safely retrieve the first value from a metadata field.
    """

    try:
        value = audio.get(key)

        if not value:
            return None

        if isinstance(value, list):
            return str(value[0])

        return str(value)

    except Exception:
        return None