import re


# Patterns that commonly indicate download-site/source noise.
NOISE_PATTERNS = [
    r"\s*-\s*PagalNew\b",
    r"\s*-\s*SenSongsMp3\.Co\b",
    r"\s*::\s*SenSongsMp3\.Co\b",
    r"\s*-\s*SenSongsMp3\b",
    r"\s*\(www\.SenSongsMp3\.co\)\b",
    r"\s*\(www\.SenSongsMp3\.com\)\b",
    r"\s*\(PenduJatt\.Com\.Se\)\b",
]


def clean_title(title: str) -> str:
    """
    Conservatively remove common download/source-site noise
    from a track title.

    Does not attempt to infer or rewrite the actual song title.
    """

    if not title:
        return title

    cleaned = title.strip()

    for pattern in NOISE_PATTERNS:
        cleaned = re.sub(
            pattern,
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

    # Remove leading track numbers such as:
    # "02 - Naalona Pongenu"
    # "04 - Mrogindi"
    cleaned = re.sub(
        r"^\s*\d{1,3}\s*[-_.]\s*",
        "",
        cleaned,
    )

    # Remove repeated whitespace.
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip(" -:_")


def normalize_metadata(metadata: dict) -> dict:
    """
    Normalize extracted metadata while preserving the original
    information whenever possible.
    """

    normalized = metadata.copy()

    normalized["title"] = clean_title(
        metadata.get("title", "")
    )

    artist = metadata.get("artist")

    if artist:
        normalized["artist"] = artist.strip()
    else:
        normalized["artist"] = "Unknown"

    album = metadata.get("album")

    if album:
        normalized["album"] = album.strip()

    return normalized