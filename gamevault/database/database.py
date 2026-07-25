"""
GameVault - Database Module

Verwaltet die SQLite-Datenbank.
"""

import sqlite3
from pathlib import Path
from typing import Optional

from gamevault.models.game import Game


class Database:
    """Verwaltet die Verbindung zur SQLite-Datenbank."""

    def __init__(self, database_path: Path | None = None) -> None:
        # Projektwurzel bestimmen
        self.project_root = Path(__file__).resolve().parent.parent.parent

        # Datenbankpfad
        self.database_path = database_path or self.project_root / "data" / "gamevault.db"

        # SQLite-Verbindung
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Stellt die Verbindung zur Datenbank her."""

        # Datenordner sicherstellen
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        # Verbindung öffnen (Datei wird bei Bedarf automatisch erstellt)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

        print(f"SQLite verbunden: {self.database_path}")

    def create_tables(self) -> None:
        """Erstellt die grundlegenden Tabellen der GameVault-Sammlung."""

        if self.connection is None:
            raise RuntimeError("Keine Datenbankverbindung vorhanden.")

        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                edition TEXT,
                platform TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ownership (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version_id INTEGER NOT NULL,
                connector TEXT NOT NULL,
                source_id TEXT,
                installed INTEGER NOT NULL DEFAULT 0,
                install_path TEXT,
                last_sync TEXT,
                FOREIGN KEY (version_id) REFERENCES versions(id) ON DELETE CASCADE
            );
            """
        )
        self.connection.commit()

    def add_game(self, title: str, release_year: int | None = None) -> Game:
        """Speichert einen neuen zentralen Spieleintrag."""

        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Ein Spieltitel darf nicht leer sein.")

        connection = self._require_connection()
        cursor = connection.execute(
            "INSERT INTO games (title, release_year) VALUES (?, ?)",
            (normalized_title, release_year),
        )
        connection.commit()

        game = self.get_game(cursor.lastrowid)
        if game is None:
            raise RuntimeError("Das gespeicherte Spiel konnte nicht gelesen werden.")

        return game

    def get_game(self, game_id: int) -> Game | None:
        """Liest ein Spiel anhand seiner internen GameVault-ID."""

        row = self._require_connection().execute(
            "SELECT id, title, release_year FROM games WHERE id = ?",
            (game_id,),
        ).fetchone()

        if row is None:
            return None

        return Game(
            id=row["id"],
            title=row["title"],
            release_year=row["release_year"],
        )

    def _require_connection(self) -> sqlite3.Connection:
        """Gibt die aktive Verbindung zurück oder meldet einen Programmfehler."""

        if self.connection is None:
            raise RuntimeError("Keine Datenbankverbindung vorhanden.")

        return self.connection

    def disconnect(self) -> None:
        """Schließt die Datenbankverbindung."""

        if self.connection:
            self.connection.close()
            self.connection = None
            print("SQLite-Verbindung geschlossen.")
