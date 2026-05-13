import sys
import os
from PyQt5.QtWidgets import QApplication

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from core.logger import log_info

def run_gui():
    """Main entry point to start the PyQt5 GUI application."""
    log_info("Starting NOVA GUI Application")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    exit_code = app.exec_()
    log_info(f"NOVA GUI Application Exited with code: {exit_code}")
    sys.exit(exit_code)
