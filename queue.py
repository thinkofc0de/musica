from typing import List, Dict, Any

from core.models import MusicaTrack
from core.music.music_profile import build_music_profile
from core.music.intention import intention_score


# ============================================================
# QUEUE OPTIMIZER
# ============================================================

def rank_tracks(
    tracks: List[MusicaTrack],
    intention: str
) -> List[Dict[str, Any]]:
    """
    Rank tracks according to how well their MusicProfile
    matches the requested intention.

    Returns a list of dictionaries containing:

        {
            "track": MusicaTrack,
            "score": float,
            "profile": dict
        }

    Higher score = better match.
    """

    ranked = []

    for track in tracks:

        profile = build_music_profile(track)

        score = intention_score(
            profile.to_dict(),
            intention
        )

        ranked.append({
            "track": track,
            "score": score,
            "profile": profile.to_dict(),
        })

    # Highest compatibility first
    ranked.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ranked


# ============================================================
# BUILD QUEUE
# ============================================================

def build_queue(
    tracks: List[MusicaTrack],
    intention: str,
    limit: int | None = None
) -> List[MusicaTrack]:
    """
    Build an ordered Musica queue for an intention.

    The original track collection is not modified.

    Args:
        tracks:
            Available MusicaTrack objects.

        intention:
            Target intention such as:
            DEEP_FOCUS, GENERAL_WORK, etc.

        limit:
            Optional maximum number of tracks.

    Returns:
        Ordered list of MusicaTrack objects.
    """

    ranked = rank_tracks(
        tracks,
        intention
    )

    if limit is not None:
        ranked = ranked[:limit]

    return [
        item["track"]
        for item in ranked
    ]


# ============================================================
# DEBUG / EXPLANATION
# ============================================================

def explain_queue(
    tracks: List[MusicaTrack],
    intention: str
) -> List[Dict[str, Any]]:
    """
    Return queue information useful for debugging,
    UI display, or later agent reasoning.

    This does NOT modify the queue.
    """

    ranked = rank_tracks(
        tracks,
        intention
    )

    result = []

    for position, item in enumerate(ranked, start=1):

        track = item["track"]

        result.append({
            "position": position,
            "title": track.title,
            "artist": track.artist,
            "intention": intention.upper(),
            "score": item["score"],
            "profile": item["profile"],
        })

    return result