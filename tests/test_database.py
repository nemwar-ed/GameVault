"""Automatische Tests für die GameVault-Datenbankschicht."""

import tempfile
import unittest
from pathlib import Path

from gamevault.database.database import Database


class DatabaseTests(unittest.TestCase):
    """Prüft die grundlegende Speicherung von Spielen."""

    def test_add_game_and_get_game(self) -> None:
        """Ein gespeichertes Spiel kann über seine ID wieder gelesen werden."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "test_gamevault.db")
            database.connect()

            saved_game = database.add_game("Diablo II", 2000)
            loaded_game = database.get_game(saved_game.id)

            database.disconnect()

        self.assertEqual(loaded_game, saved_game)

    def test_add_version_and_get_versions(self) -> None:
        """Eine Spiele-Version bleibt mit ihrem zentralen Spiel verknüpft."""

        with tempfile.TemporaryDirectory() as temporary_directory:
            database = Database(Path(temporary_directory) / "test_gamevault.db")
            database.connect()

            game = database.add_game("Diablo II", 2000)
            saved_version = database.add_version(
                game.id,
                platform="PC",
                edition="Lord of Destruction",
            )
            versions = database.get_versions(game.id)

            database.disconnect()

        self.assertEqual(versions, [saved_version])
