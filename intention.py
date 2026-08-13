from typing import Dict, Any


# ============================================================
# INTENTION PROFILES
# ============================================================

INTENTION_TARGETS = {
    "DEEP_FOCUS": {
        "energy": 0.45,
        "intensity": 0.35,
        "calm": 0.70,
        "focus": 0.90,
    },

    "GENERAL_WORK": {
        "energy": 0.55,
        "intensity": 0.45,
        "calm": 0.60,
        "focus": 0.75,
    },

    "ENERGY_BOOST": {
        "energy": 0.80,
        "intensity": 0.75,
        "calm": 0.30,
        "focus": 0.45,
    },

    "RELAXATION": {
        "energy": 0.35,
        "intensity": 0.25,
        "calm": 0.85,
        "focus": 0.65,
    },

    "WIND_DOWN": {
        "energy": 0.30,
        "intensity": 0.20,
        "calm": 0.90,
        "focus": 0.55,
    },
}


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def _distance(profile: Dict[str, float],
              target: Dict[str, float]) -> float:
    """
    Calculate how far a music profile is from an intention target.

    Lower score = better match.
    """

    dimensions = [
        "energy",
        "intensity",
        "calm",
        "focus",
    ]

    total = 0.0

    for dimension in dimensions:
        actual = float(profile.get(dimension, 0.0))
        desired = float(target.get(dimension, 0.0))

        total += abs(actual - desired)

    return total


# ============================================================
# BEST INTENTION
# ============================================================

def classify_intention(profile: Dict[str, float]) -> Dict[str, Any]:
    """
    Determine which listening intention best matches a music profile.

    Returns:
        {
            "intention": "...",
            "score": 0.0,
            "alternatives": [...]
        }
    """

    results = []

    for intention, target in INTENTION_TARGETS.items():

        score = _distance(profile, target)

        results.append({
            "intention": intention,
            "score": round(score, 4),
        })

    # Lower distance means better match
    results.sort(key=lambda x: x["score"])

    best = results[0]

    return {
        "intention": best["intention"],
        "score": best["score"],
        "alternatives": results[1:],
    }


# ============================================================
# INTENTION COMPATIBILITY
# ============================================================

def intention_score(
    profile: Dict[str, float],
    intention: str
) -> float:
    """
    Return a normalized compatibility score.

    1.0 = excellent match
    0.0 = poor match
    """

    intention = intention.upper()

    if intention not in INTENTION_TARGETS:
        raise ValueError(
            f"Unknown intention: {intention}. "
            f"Available intentions: {list(INTENTION_TARGETS.keys())}"
        )

    distance = _distance(
        profile,
        INTENTION_TARGETS[intention]
    )

    # Maximum possible distance across 4 dimensions = 4
    score = 1.0 - (distance / 4.0)

    return round(max(0.0, min(1.0, score)), 4)


# ============================================================
# HUMAN-READABLE INTENTION
# ============================================================

def explain_intention(intention: str) -> str:
    """
    Convert an internal intention name into a human-readable label.
    """

    descriptions = {
        "DEEP_FOCUS":
            "Deep Focus — low distraction and sustained concentration",

        "GENERAL_WORK":
            "General Work — balanced background music for productivity",

        "ENERGY_BOOST":
            "Energy Boost — energetic music for increasing momentum",

        "RELAXATION":
            "Relaxation — calm music for reducing mental intensity",

        "WIND_DOWN":
            "Wind Down — very calm music for slowing down",
    }

    intention = intention.upper()

    return descriptions.get(
        intention,
        "Unknown intention"
    )