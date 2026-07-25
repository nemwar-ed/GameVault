"""
GameVault - Database Module

Verwaltet die SQLite-Datenbank.
"""

import sqlite3
from pathlib import Path
from typing import Optional

from gamevault.models.game import Game
from gamevault.models.game_version import GameVersion
from gamevault.models.ownership import Ownership


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

    def add_version(
        self,
        game_id: int,
        platform: str,
        edition: str | None = None,
    ) -> GameVersion:
        """Speichert eine Edition auf einer Plattform für ein Spiel."""

        normalized_platform = platform.strip()
        if not normalized_platform:
            raise ValueError("Eine Plattform darf nicht leer sein.")

        normalized_edition = edition.strip() if edition else None
        connection = self._require_connection()
        cursor = connection.execute(
            "INSERT INTO versions (game_id, edition, platform) VALUES (?, ?, ?)",
            (game_id, normalized_edition, normalized_platform),
        )
        connection.commit()

        row = connection.execute(
            "SELECT id, game_id, edition, platform FROM versions WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Die gespeicherte Version konnte nicht gelesen werden.")

        return self._create_game_version(row)

    def get_versions(self, game_id: int) -> list[GameVersion]:
        """Liest alle Versionen eines Spiels in ihrer Erstellungsreihenfolge."""

        rows = self._require_connection().execute(
            """
            SELECT id, game_id, edition, platform
            FROM versions
            WHERE game_id = ?
            ORDER BY id
            """,
            (game_id,),
        ).fetchall()

        return [self._create_game_version(row) for row in rows]

    def add_ownership(
        self,
        version_id: int,
        connector: str,
        source_id: str | None = None,
        installed: bool = False,
        install_path: str | None = None,
    ) -> Ownership:
        """Speichert eine Quelle, über die eine Spielversion vorhanden ist."""

        normalized_connector = connector.strip()
        if not normalized_connector:
            raise ValueError("Eine Besitzquelle darf nicht leer sein.")

        normalized_source_id = source_id.strip() if source_id else None
        normalized_install_path = install_path.strip() if install_path else None
        connection = self._require_connection()
        cursor = connection.execute(
            """
            INSERT INTO ownership (
                version_id,
                connector,
                source_id,
                installed,
                install_path
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                version_id,
                normalized_connector,
                normalized_source_id,
                int(installed),
                normalized_install_path,
            ),
        )
        connection.commit()

        row = connection.execute(
            """
            SELECT id, version_id, connector, source_id, installed, install_path
            FROM ownership
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        if row is None:
            raise RuntimeError("Der gespeicherte Besitz konnte nicht gelesen werden.")

        return self._create_ownership(row)

    def get_ownership(self, version_id: int) -> list[Ownership]:
        """Liest alle Besitzquellen einer Spielversion."""

        rows = self._require_connection().execute(
            """
            SELECT id, version_id, connector, source_id, installed, install_path
            FROM ownership
            WHERE version_id = ?
            ORDER BY id
            """,
            (version_id,),
        ).fetchall()

        return [self._create_ownership(row) for row in rows]

    @staticmethod
    def _create_game_version(row: sqlite3.Row) -> GameVersion:
        """Erzeugt ein Version-Modell aus einer SQLite-Zeile."""

        return GameVersion(
            id=row["id"],
            game_id=row["game_id"],
            edition=row["edition"],
            platform=row["platform"],
        )

    @staticmethod
    def _create_ownership(row: sqlite3.Row) -> Ownership:
        """Erzeugt ein Besitz-Modell aus einer SQLite-Zeile."""

        return Ownership(
            id=row["id"],
            version_id=row["version_id"],
            connector=row["connector"],
            source_id=row["source_id"],
            installed=bool(row["installed"]),
            install_path=row["install_path"],
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
