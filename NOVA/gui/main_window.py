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
from gui.worker import CommandWorker, VoiceWorker, WakeWorker, ContinuousVoiceWorker, confirmation_bridge
from core.safety import register_gui_confirmation_callback
from memory import memory_db

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.GUI_WINDOW_TITLE)
        self.resize(1000, 720) # Modern dashboard width and height
        self.setStyleSheet(DARK_STYLE)
        
        # Register the bridge with the safety module
        register_gui_confirmation_callback(confirmation_bridge.confirm)
        
        # Connect the bridge's signal to our handler with BlockingQueuedConnection
        confirmation_bridge.request_signal.connect(self.show_confirmation_dialog, Qt.BlockingQueuedConnection)
        
        self.init_ui()
        self.update_previews()
        
        self.wake_worker = None
        self.continuous_voice_worker = None

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with outer margins (16px) and spacing (14px)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # --- Left Panel: Chat (70% stretch) ---
        left_panel = QFrame()
        left_panel.setObjectName("ChatPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        self.header_title = QLabel("NOVA")
        self.header_title.setObjectName("HeaderTitle")
        left_layout.addWidget(self.header_title)

        self.status_label = QLabel("Status: <span style='color: #20E6A8;'>Idle</span>")
        self.status_label.setObjectName("StatusLabel")
        left_layout.addWidget(self.status_label)

        divider = QFrame()
        divider.setObjectName("HeaderDivider")
        left_layout.addWidget(divider)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("ChatDisplay")
        left_layout.addWidget(self.chat_display)

        # Input row with spacing (10px)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("CommandInput")
        self.input_field.setPlaceholderText("Ask NOVA anything...")
        self.input_field.returnPressed.connect(self.handle_send)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setToolTip("Send command")
        self.send_btn.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_btn)

        self.voice_btn = QPushButton("🎙")
        self.voice_btn.setObjectName("VoiceBtn")
        self.voice_btn.setToolTip("Voice input")
        self.voice_btn.clicked.connect(self.handle_voice)
        input_layout.addWidget(self.voice_btn)

        left_layout.addLayout(input_layout)
        main_layout.addWidget(left_panel, 7)

        # --- Right Panel: Sidebar (30% stretch) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        # A. Quick Actions card
        actions_card = QFrame()
        actions_card.setObjectName("QuickActionsCard")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setContentsMargins(16, 16, 16, 16)
        actions_layout.setSpacing(12)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setObjectName("CardTitle")
        actions_layout.addWidget(actions_title)
        
        btn_status = QPushButton("System Status")
        btn_status.setObjectName("PrimaryActionBtn")
        btn_status.clicked.connect(lambda: self.submit_command("system status"))
        actions_layout.addWidget(btn_status)

        btn_screen = QPushButton("Read Screen")
        btn_screen.setObjectName("SecondaryActionBtn")
        btn_screen.clicked.connect(lambda: self.submit_command("read my screen"))
        actions_layout.addWidget(btn_screen)

        btn_wake = QPushButton("Start Wake Mode")
        btn_wake.setObjectName("SecondaryActionBtn")
        btn_wake.clicked.connect(self.toggle_wake_mode)
        self.wake_btn = btn_wake
        actions_layout.addWidget(btn_wake)

        right_layout.addWidget(actions_card)

        # B. Recent Memory card
        if config.GUI_SHOW_MEMORY_PANEL:
            memory_card = QFrame()
            memory_card.setObjectName("MemoryCard")
            self.memory_layout = QVBoxLayout(memory_card)
            self.memory_layout.setContentsMargins(16, 16, 16, 16)
            self.memory_layout.setSpacing(10)
            
            memory_title = QLabel("Recent Memory")
            memory_title.setObjectName("CardTitle")
            self.memory_layout.addWidget(memory_title)
            
            # The actual previews (MemoryMiniCards) will be placed inside this layout in update_previews
            right_layout.addWidget(memory_card, 1)

        # C. Live Logs card
        if config.GUI_SHOW_LOG_PANEL:
            logs_card = QFrame()
            logs_card.setObjectName("LogsCard")
            logs_layout = QVBoxLayout(logs_card)
            logs_layout.setContentsMargins(16, 16, 16, 16)
            logs_layout.setSpacing(10)
            
            logs_title = QLabel("Live Logs")
            logs_title.setObjectName("CardTitle")
            logs_layout.addWidget(logs_title)
            
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)
            self.log_display.setObjectName("LogPreview")
            logs_layout.addWidget(self.log_display)
            
            right_layout.addWidget(logs_card, 1)

        main_layout.addWidget(right_panel, 3)

    def append_chat(self, sender, message):
        if sender == "You":
            html = f"<div style='margin-bottom: 12px;'><span style='color: #E6EDF3; font-weight: bold;'>You:</span> <span style='color: #B8C0CC;'>{message}</span></div>"
        elif sender == "NOVA":
            html = f"<div style='margin-bottom: 12px;'><span style='color: #20D9FF; font-weight: bold;'>NOVA:</span> <span style='color: #E6EDF3;'>{message}</span></div>"
        else: # ERROR or other status reporting
            html = f"<div style='margin-bottom: 12px;'><span style='color: #FF4A4A; font-weight: bold;'>{sender}:</span> <span style='color: #FF8888;'>{message}</span></div>"
        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)

    def handle_send(self):
        query = self.input_field.text().strip()
        if query:
            self.input_field.clear()
            self.submit_command(query)

    def submit_command(self, query):
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.append_chat("NOVA", "Please wait until the current command finishes processing.")
            return

        self.append_chat("You", query)
        self.worker = CommandWorker(query)
        self.worker.status_update.connect(self.update_status)
        self.worker.finished.connect(self.on_command_finished)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def handle_voice(self):
        if hasattr(self, 'voice_worker') and self.voice_worker and self.voice_worker.isRunning():
            return
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.append_chat("NOVA", "Please wait until the current command finishes processing.")
            return

        self.append_chat("NOVA", "Listening... please speak now.")
        self.voice_worker = VoiceWorker()
        self.voice_worker.status_update.connect(self.update_status)
        self.voice_worker.recognized.connect(self.on_voice_recognized)
        self.voice_worker.error_occurred.connect(self.handle_error)
        self.voice_worker.start()

    def toggle_wake_mode(self):
        if self.continuous_voice_worker and self.continuous_voice_worker.isRunning():
            self.continuous_voice_worker.stop()
            self.continuous_voice_worker.wait(2000)
            self.continuous_voice_worker = None
            self.wake_btn.setText("Start Wake Mode")
            self.update_status("Idle")
        else:
            if self.continuous_voice_worker is not None and self.continuous_voice_worker.isRunning():
                return

            self.continuous_voice_worker = ContinuousVoiceWorker()
            self.continuous_voice_worker.status.connect(self.update_status)
            self.continuous_voice_worker.recognized.connect(self.on_continuous_recognized)
            self.continuous_voice_worker.response.connect(self.on_continuous_response)
            self.continuous_voice_worker.log.connect(self.log_message)
            self.continuous_voice_worker.error.connect(self.handle_error)
            self.continuous_voice_worker.start()
            self.wake_btn.setText("Stop Wake Mode")
            self.update_status("Listening...")

    @pyqtSlot(str)
    def on_continuous_recognized(self, query):
        self.append_chat("You", query)

    @pyqtSlot(str, str)
    def on_continuous_response(self, query, response):
        self.append_chat("NOVA", response)
        self.update_previews()

    @pyqtSlot(str)
    def log_message(self, message):
        import logging
        logging.info(message)
        self.update_previews()


    @pyqtSlot(str)
    def update_status(self, status):
        color = "#20E6A8" if status.lower() == "idle" else "#20D9FF"
        self.status_label.setText(f"Status: <span style='color: {color};'>{status}</span>")

    @pyqtSlot(dict)
    def on_voice_recognized(self, result):
        if result["success"]:
            query = result["text"]
            self.submit_command(query)
        else:
            err_type = result.get("error_type")
            msg = result.get("message", "I did not hear anything.")
            
            if err_type == "timeout":
                self.append_chat("NOVA", "I did not hear anything. Please check your microphone or speak closer.")
            elif err_type == "unknown_speech":
                self.append_chat("NOVA", "I heard something, but could not understand it.")
            elif err_type == "request_error":
                self.append_chat("NOVA", "Speech recognition service failed. Check your internet connection.")
            elif err_type in ["microphone_error", "pyaudio_missing"]:
                self.append_chat("NOVA", "Microphone is unavailable. Check Windows input settings.")
            else:
                self.append_chat("NOVA", msg)
                
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
        # Update Memory Mini-Cards
        if hasattr(self, 'memory_layout'):
            # Clear previous items (keeping the title label)
            for i in reversed(range(self.memory_layout.count())):
                widget = self.memory_layout.itemAt(i).widget()
                if widget and widget.objectName() != "CardTitle":
                    widget.setParent(None)
                    widget.deleteLater()
            
            # Fetch and render the top 2 recent interactions as mini-cards
            interactions = memory_db.get_recent_interactions(2)
            if interactions:
                for _, cmd, resp, _ in reversed(interactions):
                    card = QFrame()
                    card.setObjectName("MemoryMiniCard")
                    card_layout = QVBoxLayout(card)
                    card_layout.setContentsMargins(10, 10, 10, 10)
                    card_layout.setSpacing(4)
                    
                    cmd_label = QLabel(f"<b>Query:</b> {cmd}")
                    cmd_label.setWordWrap(True)
                    cmd_label.setStyleSheet("color: #E6EDF3; font-size: 8.5pt; background: transparent; border: none;")
                    
                    short_resp = resp[:90] + "..." if len(resp) > 90 else resp
                    resp_label = QLabel(f"<b>NOVA:</b> {short_resp}")
                    resp_label.setWordWrap(True)
                    resp_label.setStyleSheet("color: #B8C0CC; font-size: 8.5pt; background: transparent; border: none;")
                    
                    card_layout.addWidget(cmd_label)
                    card_layout.addWidget(resp_label)
                    self.memory_layout.addWidget(card)
            else:
                empty_label = QLabel("No recent memory yet.")
                empty_label.setStyleSheet("color: #8A93A3; font-style: italic; font-size: 9pt; background: transparent; border: none;")
                empty_label.setAlignment(Qt.AlignCenter)
                self.memory_layout.addWidget(empty_label)
        
        # Update Live Logs terminal box
        if hasattr(self, 'log_display'):
            try:
                if os.path.exists(config.LOG_FILE):
                    with open(config.LOG_FILE, "r") as f:
                        lines = f.readlines()[-15:]
                        cleaned_lines = []
                        for line in lines:
                            parts = line.split(" - ")
                            if len(parts) >= 3:
                                time_str = parts[0].split(" ")[1].split(",")[0]
                                msg = " - ".join(parts[2:]).strip()
                                cleaned_lines.append(f"[{time_str}] {msg}")
                            else:
                                cleaned_lines.append(line.strip())
                        self.log_display.setPlainText("\n".join(cleaned_lines))
                        self.log_display.moveCursor(QTextCursor.End)
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

    def closeEvent(self, event):
        if hasattr(self, 'continuous_voice_worker') and self.continuous_voice_worker and self.continuous_voice_worker.isRunning():
            self.continuous_voice_worker.stop()
            self.continuous_voice_worker.wait(2000)
        if hasattr(self, 'voice_worker') and self.voice_worker and self.voice_worker.isRunning():
            self.voice_worker.wait()
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.wait()
        event.accept()
