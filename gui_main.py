import sys
import os
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Load QSS
    try:
        qss_path = resource_path(os.path.join("gui", "style.qss"))
        with open(qss_path, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Could not load stylesheet: {e}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
