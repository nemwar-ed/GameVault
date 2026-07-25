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

Die spätere Dublettenerkennung wird getrennt entwickelt. Sie darf nicht allein
auf einem ähnlichen Titel beruhen, weil Editionen und gleichnamige Spiele bewusst
geprüft werden müssen.
