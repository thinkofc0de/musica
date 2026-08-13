from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf


def extract_audio_features(file_path: str) -> Optional[dict]:
    """
    Extract basic, measurable audio features from a music file.

    V1 deliberately avoids librosa/numba.

    Returns:
        dict containing basic audio characteristics,
        or None if the file cannot be analyzed.
    """

    path = Path(file_path)

    if not path.exists():
        print(f"[Audio Features] File not found: {path}")
        return None

    try:
        # Read audio file
        audio, sample_rate = sf.read(
            str(path),
            always_2d=True,
        )

        if audio.size == 0:
            print(f"[Audio Features] Empty audio file: {path.name}")
            return None

        # Number of channels
        channels = audio.shape[1]

        # Convert to mono for analysis
        mono = audio.mean(axis=1)

        # Duration
        duration = len(mono) / sample_rate

        # RMS energy
        rms_energy = float(
            np.sqrt(np.mean(np.square(mono)))
        )

        # Peak amplitude
        peak_amplitude = float(
            np.max(np.abs(mono))
        )

        # Zero crossing rate
        signs = np.signbit(mono)

        zero_crossings = np.count_nonzero(
            signs[1:] != signs[:-1]
        )

        zero_crossing_rate = float(
            zero_crossings / max(len(mono) - 1, 1)
        )

        return {
            "duration": round(duration, 3),
            "sample_rate": int(sample_rate),
            "channels": int(channels),
            "rms_energy": round(rms_energy, 6),
            "peak_amplitude": round(peak_amplitude, 6),
            "zero_crossing_rate": round(
                zero_crossing_rate,
                6,
            ),
        }

    except Exception as e:
        print(
            f"[Audio Features] Could not analyze "
            f"{path.name}: {e}"
        )
        return None