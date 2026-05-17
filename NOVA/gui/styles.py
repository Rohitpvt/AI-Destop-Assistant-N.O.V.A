DARK_STYLE = """
QMainWindow {
    background-color: #0B111C;
}

QWidget {
    color: #E6EDF3;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
}

/* Left Chat Panel */
QFrame#ChatPanel {
    background-color: #111622;
    border: 1px solid #1E2E44;
    border-radius: 16px;
}

/* Chat display area */
QTextEdit#ChatDisplay {
    background-color: transparent;
    border: none;
    font-size: 10pt;
    color: #E6EDF3;
}

/* Header section label styling */
QLabel#HeaderTitle {
    font-size: 24pt;
    font-weight: bold;
    color: white;
    background: transparent;
    border: none;
}

QLabel#StatusLabel {
    font-size: 11pt;
    font-weight: bold;
    background: transparent;
    border: none;
}

QFrame#HeaderDivider {
    border: none;
    background-color: #1E2E44;
    max-height: 1px;
    min-height: 1px;
}

/* Input Area styling */
QLineEdit#CommandInput {
    background-color: #0D111A;
    border: 1.5px solid #24445A;
    border-radius: 10px;
    padding: 10px 14px;
    color: #E6EDF3;
    font-size: 10pt;
}

QLineEdit#CommandInput:focus {
    border: 1.5px solid #20D9FF;
    background-color: #0F1522;
}

QPushButton#SendBtn {
    background-color: #172535;
    border: 1.5px solid #24445A;
    border-radius: 8px;
    color: #20D9FF;
    font-weight: bold;
    padding: 8px 18px;
    font-size: 9.5pt;
}

QPushButton#SendBtn:hover {
    background-color: #1A314A;
    border-color: #20D9FF;
}

QPushButton#VoiceBtn {
    background-color: #172535;
    border: 1.5px solid #20D9FF;
    border-radius: 8px;
    color: #20D9FF;
    font-weight: bold;
    padding: 8px 12px;
    font-size: 14pt;
}

QPushButton#VoiceBtn:hover {
    background-color: #1A314A;
    border-color: #36E0FF;
}

/* Right Sidebar Cards */
QFrame#QuickActionsCard, QFrame#MemoryCard, QFrame#LogsCard {
    background-color: #111622;
    border: 1px solid #1E2E44;
    border-radius: 14px;
}

QLabel#CardTitle {
    font-size: 11pt;
    font-weight: bold;
    color: #E6EDF3;
    background: transparent;
    border: none;
    margin-bottom: 6px;
}

/* Card Buttons */
QPushButton#PrimaryActionBtn {
    background-color: rgba(32, 217, 255, 0.08);
    border: 1.5px solid #20D9FF;
    border-radius: 8px;
    color: #20D9FF;
    font-weight: bold;
    padding: 9px 15px;
    font-size: 9.5pt;
}

QPushButton#PrimaryActionBtn:hover {
    background-color: rgba(32, 217, 255, 0.16);
    border-color: #36E0FF;
    color: #36E0FF;
}

QPushButton#SecondaryActionBtn {
    background-color: transparent;
    border: 1.5px solid #24445A;
    border-radius: 8px;
    color: #8A93A3;
    font-weight: bold;
    padding: 9px 15px;
    font-size: 9.5pt;
}

QPushButton#SecondaryActionBtn:hover {
    border-color: #20D9FF;
    color: #20D9FF;
    background-color: rgba(32, 217, 255, 0.05);
}

/* Memory Cards */
QFrame#MemoryMiniCard {
    background-color: rgba(32, 40, 60, 0.35);
    border: 1px solid #1E2E44;
    border-radius: 8px;
}

/* Live Logs Console */
QTextEdit#LogPreview {
    background-color: #080D16;
    border: 1px solid #1A283C;
    border-radius: 6px;
    color: #8A93A3;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8.5pt;
    padding: 6px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #1E2E44;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #20D9FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
