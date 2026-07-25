\# Datenbankmodell

GameVault verwendet eine einzelne SQLite-Datenbank unter `data/gamevault.db`.

## Hierarchie

1. **Spiel** – der eigentliche Titel, beispielsweise *Diablo II*.
2. **Version** – Edition oder Veröffentlichung des Spiels auf einer Plattform.
3. **Besitz** – eine Quelle, über die diese Version vorhanden ist.

Ein Spiel wird nur einmal gespeichert. Mehrere Editionen, Plattformen und Quellen
werden darunter verknüpft.

## Tabellen

- `games`: Titel und Erscheinungsjahr.
- `versions`: Edition und Plattform eines Spiels.
- `ownership`: Quelle, Quell-ID sowie Installationsinformationen einer Version.

## Aktuelle Datenbankfunktionen

- `add_game(title, release_year)`: Speichert einen zentralen Spieleintrag.
- `get_game(game_id)`: Liest einen Spieleintrag über seine GameVault-ID.
- `add_version(game_id, platform, edition)`: Speichert eine Edition auf einer
  Plattform unter einem Spiel.
- `get_versions(game_id)`: Liest alle Versionen eines Spiels.
- `add_ownership(...)`: Speichert eine Besitzquelle einer Spielversion.
- `get_ownership(version_id)`: Liest alle Besitzquellen einer Spielversion.

Die spätere Dublettenerkennung wird getrennt entwickelt. Sie darf nicht allein
auf einem ähnlichen Titel beruhen, weil Editionen und gleichnamige Spiele bewusst
geprüft werden müssen.
