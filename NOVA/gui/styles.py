DARK_STYLE = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    color: #E0E0E0;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
}

QFrame#ChatPanel {
    background-color: #1E1E1E;
    border-radius: 10px;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QLineEdit {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 5px;
    padding: 8px;
    color: white;
}

QLineEdit:focus {
    border: 1px solid #00A8FF;
}

QPushButton {
    background-color: #00A8FF;
    color: white;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0097E6;
}

QPushButton:pressed {
    background-color: #0084CC;
}

QPushButton#VoiceBtn {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
}

QPushButton#VoiceBtn:hover {
    background-color: #3D3D3D;
}

QLabel#StatusLabel {
    color: #00A8FF;
    font-weight: bold;
}

QTextEdit#LogPreview, QTextEdit#MemoryPreview {
    background-color: #181818;
    border: 1px solid #2D2D2D;
    border-radius: 5px;
    color: #AAAAAA;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}

QGroupBox {
    font-weight: bold;
    border: 1px solid #2D2D2D;
    margin-top: 1.1em;
    padding-top: 0.5em;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QScrollBar:vertical {
    border: none;
    background: #1E1E1E;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3D3D3D;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
