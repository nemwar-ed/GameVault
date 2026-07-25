"""Datenmodell für eine Besitzquelle einer Spielversion."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Ownership:
    """Repräsentiert den Besitz einer Spielversion über eine Quelle."""

    id: int
    version_id: int
    connector: str
    source_id: str | None
    installed: bool
    install_path: str | None
