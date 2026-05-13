from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, 
                             QScrollArea, QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor
import os
import sys

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from gui.styles import DARK_STYLE
from gui.worker import CommandWorker, VoiceWorker, WakeWorker, confirmation_bridge
from core.safety import register_gui_confirmation_callback
from memory import memory_db

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.GUI_WINDOW_TITLE)
        self.resize(config.GUI_WIDTH, config.GUI_HEIGHT)
        self.setStyleSheet(DARK_STYLE)
        
        # Register the bridge with the safety module
        register_gui_confirmation_callback(confirmation_bridge.confirm)
        
        # Connect the bridge's signal to our handler with BlockingQueuedConnection
        confirmation_bridge.request_signal.connect(self.show_confirmation_dialog, Qt.BlockingQueuedConnection)
        
        self.init_ui()
        self.update_previews()
        
        self.wake_worker = None

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Left Panel: Chat ---
        left_panel = QFrame()
        left_panel.setObjectName("ChatPanel")
        left_layout = QVBoxLayout(left_panel)

        self.status_label = QLabel("Status: Idle")
        self.status_label.setObjectName("StatusLabel")
        left_layout.addWidget(self.status_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        left_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.returnPressed.connect(self.handle_send)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_btn)

        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setObjectName("VoiceBtn")
        self.voice_btn.setToolTip("Voice Listen")
        self.voice_btn.clicked.connect(self.handle_voice)
        input_layout.addWidget(self.voice_btn)

        left_layout.addLayout(input_layout)
        main_layout.addWidget(left_panel, 3)

        # --- Right Panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        btn_status = QPushButton("System Status")
        btn_status.clicked.connect(lambda: self.submit_command("system status"))
        actions_layout.addWidget(btn_status)

        btn_screen = QPushButton("Read Screen")
        btn_screen.clicked.connect(lambda: self.submit_command("read my screen"))
        actions_layout.addWidget(btn_screen)

        btn_wake = QPushButton("Start Wake Mode")
        btn_wake.clicked.connect(self.toggle_wake_mode)
        self.wake_btn = btn_wake
        actions_layout.addWidget(btn_wake)

        right_layout.addWidget(actions_group)

        if config.GUI_SHOW_MEMORY_PANEL:
            memory_group = QGroupBox("Recent Memory")
            memory_layout = QVBoxLayout(memory_group)
            self.memory_display = QTextEdit()
            self.memory_display.setReadOnly(True)
            self.memory_display.setObjectName("MemoryPreview")
            memory_layout.addWidget(self.memory_display)
            right_layout.addWidget(memory_group, 1)

        if config.GUI_SHOW_LOG_PANEL:
            log_group = QGroupBox("Live Logs")
            log_layout = QVBoxLayout(log_group)
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            self.log_display.setObjectName("LogPreview")
            log_layout.addWidget(self.log_display)
            right_layout.addWidget(log_group, 1)

        main_layout.addWidget(right_panel, 2)

    def append_chat(self, sender, message):
        self.chat_display.append(f"<b>{sender}:</b> {message}")
        self.chat_display.moveCursor(QTextCursor.End)

    def handle_send(self):
        query = self.input_field.text().strip()
        if query:
            self.input_field.clear()
            self.submit_command(query)

    def submit_command(self, query):
        self.append_chat("You", query)
        self.worker = CommandWorker(query)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.on_command_finished)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_voice(self):
        self.voice_worker = VoiceWorker()
        self.voice_worker.status_update.connect(self.update_status)
        self.voice_worker.recognized.connect(self.on_voice_recognized)
        self.voice_worker.error_occurred.connect(self.handle_error)
        self.voice_worker.start()

    def toggle_wake_mode(self):
        if self.wake_worker and self.wake_worker.isRunning():
            self.wake_worker.stop()
            self.wake_btn.setText("Start Wake Mode")
            self.update_status("Idle")
        else:
            self.wake_worker = WakeWorker()
            self.wake_worker.status_update.connect(self.update_status)
            self.wake_worker.command_detected.connect(self.submit_command)
            self.wake_worker.error_occurred.connect(self.handle_error)
            self.wake_worker.start()
            self.wake_btn.setText("Stop Wake Mode")

    @pyqtSlot(str)
    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    @pyqtSlot(str)
    def on_voice_recognized(self, query):
        if query:
            self.submit_command(query)
        else:
            self.append_chat("NOVA", "I did not hear anything.")
            self.update_status("Idle")

    @pyqtSlot(str, bool)
    def on_command_finished(self, response, success):
        self.append_chat("NOVA", response)
        self.update_status("Idle")
        self.update_previews()

    @pyqtSlot(str)
    def handle_error(self, err_msg):
        self.append_chat("ERROR", err_msg)
        self.update_status("Error / Idle")
        self.update_previews()

    def update_previews(self):
        interactions = memory_db.get_recent_interactions(5)
        memory_text = ""
        for _, cmd, resp, _ in reversed(interactions):
            memory_text += f"> {cmd}\n< {resp[:50]}...\n\n"
        if hasattr(self, 'memory_display'):
            self.memory_display.setPlainText(memory_text)

        try:
            if os.path.exists(config.LOG_FILE):
                with open(config.LOG_FILE, "r") as f:
                    lines = f.readlines()[-20:]
                    self.log_display.setPlainText("".join(lines))
        except:
            pass

    @pyqtSlot(str)
    def show_confirmation_dialog(self, action_description):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmation Required")
        msg_box.setText(f"NOVA wants to: {action_description}")
        msg_box.setInformativeText("Should I proceed?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("color: white; background-color: #2D2D2D;")
        
        result = msg_box.exec_()
        confirmation_bridge.result = (result == QMessageBox.Yes)
