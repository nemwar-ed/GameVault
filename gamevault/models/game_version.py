"""Datenmodell für eine Edition auf einer bestimmten Plattform."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GameVersion:
    """Repräsentiert eine Version eines zentralen Spieleintrags."""

    id: int
    game_id: int
    edition: str | None
    platform: str
