import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

from gamevault.database.database import Database


class MainWindow(QMainWindow):
    """Hauptfenster von GameVault."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("GameVault")
        self.resize(1000, 700)

        label = QLabel("Willkommen bei GameVault!")
        label.setStyleSheet("font-size: 20px; padding: 20px;")

        self.setCentralWidget(label)


def main():
    print("GameVault startet...")

    # Datenbank initialisieren
    database = Database()
    database.connect()

    # Qt starten
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    exit_code = app.exec()

    # Datenbank sauber schließen
    database.disconnect()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
