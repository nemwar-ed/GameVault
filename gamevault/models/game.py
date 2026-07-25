"""Datenmodell für einen zentralen Spieleintrag."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    """Repräsentiert einen einzelnen Titel in der GameVault-Sammlung."""

    id: int
    title: str
    release_year: int | None
