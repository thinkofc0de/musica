from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MusicaTrack:
    """
    Common representation of a track inside Musica.

    Music sources such as Local, Spotify, YT Music, etc.
    will eventually be converted into this model.
    """

    id: str
    title: str
    artist: str
    album: Optional[str] = None

    duration: Optional[float] = None

    source: str = "unknown"
    source_id: Optional[str] = None
    playback_uri: Optional[str] = None

    language: Optional[str] = None

    audio_features: dict = field(default_factory=dict)

    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert the track into a JSON-compatible dictionary."""

        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "source": self.source,
            "source_id": self.source_id,
            "playback_uri": self.playback_uri,
            "language": self.language,
            "audio_features": self.audio_features,
            "metadata": self.metadata,
        }