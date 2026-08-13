from dataclasses import dataclass, asdict
from typing import Optional

from core.models import MusicaTrack


@dataclass
class MusicProfile:
    """
    Higher-level musical profile derived from the
    measurable features available on a MusicaTrack.

    Values are normalized to the range 0.0 - 1.0.
    """

    energy: float
    intensity: float
    calm: float
    focus: float

    def to_dict(self) -> dict:
        return asdict(self)


def _clamp(value: float) -> float:
    """
    Keep a value between 0.0 and 1.0.
    """

    return max(0.0, min(1.0, value))


def _normalize_rms(rms: Optional[float]) -> float:
    """
    Convert RMS energy into a practical 0-1 range.

    This is deliberately conservative because RMS values
    from different recordings are not directly comparable.
    """

    if rms is None:
        return 0.5

    # Approximate useful range for our current library.
    return _clamp(rms / 0.40)


def _normalize_zcr(zcr: Optional[float]) -> float:
    """
    Normalize zero-crossing rate.

    Higher ZCR generally indicates more rapid waveform
    changes and can contribute to perceived intensity.
    """

    if zcr is None:
        return 0.5

    return _clamp(zcr / 0.15)


def build_music_profile(track: MusicaTrack) -> MusicProfile:
    """
    Convert the measurable audio features of a MusicaTrack
    into a higher-level MusicProfile.
    """

    features = track.audio_features or {}

    rms = features.get("rms_energy")
    zcr = features.get("zero_crossing_rate")

    normalized_rms = _normalize_rms(rms)
    normalized_zcr = _normalize_zcr(zcr)

    # -----------------------------------------
    # Energy
    # -----------------------------------------
    #
    # Currently based only on RMS energy.
    #
    # Later this can incorporate:
    # tempo, spectral features, danceability, etc.
    #

    energy = normalized_rms

    # -----------------------------------------
    # Intensity
    # -----------------------------------------

    intensity = (
        normalized_rms * 0.7
        + normalized_zcr * 0.3
    )

    intensity = _clamp(intensity)

    # -----------------------------------------
    # Calm
    # -----------------------------------------
    #
    # This is currently a simple inverse of
    # intensity. It is NOT an emotional claim.
    #

    calm = _clamp(1.0 - intensity)

    # -----------------------------------------
    # Focus
    # -----------------------------------------
    #
    # For now, moderate energy is considered
    # more suitable for focus than extreme energy.
    #
    # This is a heuristic and will be improved later.
    #

    focus = 1.0 - abs(energy - 0.45) / 0.55

    focus = _clamp(focus)

    return MusicProfile(
        energy=round(energy, 4),
        intensity=round(intensity, 4),
        calm=round(calm, 4),
        focus=round(focus, 4),
    )