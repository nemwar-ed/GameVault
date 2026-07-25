"""
GameVault - Database Module

Verwaltet die SQLite-Datenbank.
"""

from pathlib import Path
import sqlite3


class Database:
    """Verwaltet die Verbindung zur SQLite-Datenbank."""

    def __init__(self):
        # Projektwurzel bestimmen
        self.project_root = Path(__file__).resolve().parent.parent.parent

        # Datenbankpfad
        self.database_path = self.project_root / "data" / "gamevault.db"

        # SQLite-Verbindung
        self.connection = None

    def connect(self):
        """Stellt die Verbindung zur Datenbank her."""

        # Datenordner sicherstellen
        self.database_path.parent.mkdir(exist_ok=True)

        # Verbindung öffnen (Datei wird bei Bedarf automatisch erstellt)
        self.connection = sqlite3.connect(self.database_path)

        print(f"SQLite verbunden: {self.database_path}")

    def disconnect(self):
        """Schließt die Datenbankverbindung."""

        if self.connection:
            self.connection.close()
            self.connection = None
            print("SQLite-Verbindung geschlossen.")
