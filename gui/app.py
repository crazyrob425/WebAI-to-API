#!/usr/bin/env python3
"""
WebAI-to-API Desktop GUI
A PyQt6-based desktop application for managing the WebAI-to-API backend.
"""

import sys
import os
import json
import subprocess
import threading
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox,
    QTabWidget, QGroupBox, QMessageBox, QSystemTrayIcon, QMenu,
    QFrame, QSplitter
)
from PyQt6.QtCore import QTimer, QProcess, Qt, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QAction, QIcon, QColor, QTextCursor

# Try to import requests, install if not available
try:
    import requests
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests


class ServerThread(QThread):
    """Thread for running the Python server"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    
    def __init__(self, port="6969", parent=None):
        super().__init__(parent)
        self.port = port
        self.process = None
        self.running = False
    
    def run(self):
        self.running = True
        
        # Change to project directory
        project_dir = Path(__file__).parent.parent
        os.chdir(project_dir)
        
        # Try to find poetry or python
        python_cmd = "poetry"
        
        # Start the server
        self.process = subprocess.Popen(
            [python_cmd, "run", "python", "src/run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            cwd=str(project_dir)
        )
        
        self.output_signal.emit(f"Starting server on port {self.port}...")
        
        # Read output line by line
        for line in iter(self.process.stdout.readline, ''):
            if not self.running:
                break
            if line:
                self.output_signal.emit(line.strip())
        
        self.process.stdout.close()
        self.process.wait()
        self.finished_signal.emit(self.process.returncode)
    
    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


class APIClient:
    """Simple API client for testing the backend"""
    
    def __init__(self, base_url="http://localhost:6969"):
        self.base_url = base_url
    
    def get_models(self):
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, message, model="gemini-2.5-flash"):
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": message}]
                },
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.api_client = APIClient()
        self.server_running = False
        self.setup_ui()
        self.setup_tray()
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)
        self.status_timer.start(3000)  # Check every 3 seconds
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("WebAI-to-API Desktop")
        self.setMinimumSize(800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("WebAI-to-API Desktop")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2a82da;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #888;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.server_status_label = QLabel("Server: Stopped")
        self.server_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        status_layout.addWidget(self.server_status_label)
        
        main_layout.addLayout(status_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Control Tab
        control_tab = self.create_control_tab()
        self.tab_widget.addTab(control_tab, "Control")
        
        # Settings Tab
        settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(settings_tab, "Settings")
        
        # Test Chat Tab
        chat_tab = self.create_chat_tab()
        self.tab_widget.addTab(chat_tab, "Test Chat")
        
        main_layout.addWidget(self.tab_widget)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton#start_button {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton#start_button:hover {
                background-color: #45a049;
            }
            QPushButton#stop_button {
                background-color: #f44336;
                color: white;
            }
            QPushButton#stop_button:hover {
                background-color: #da190b;
            }
            QPushButton#test_button {
                background-color: #2196F3;
                color: white;
            }
            QPushButton#send_button {
                background-color: #2a82da;
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #444;
            }
            QTabBar::tab {
                background-color: #353535;
                color: #aaa;
                padding: 8px 20px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
                color: white;
            }
        """)
    
    def create_control_tab(self) -> QWidget:
        """Create the control tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Server controls
        server_group = QGroupBox("Server Control")
        server_layout = QVBoxLayout(server_group)
        
        # Port setting
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QLineEdit("6969")
        self.port_input.setMaximumWidth(100)
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        server_layout.addLayout(port_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Server")
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_button)
        
        self.test_button = QPushButton("Test API")
        self.test_button.setObjectName("test_button")
        self.test_button.setMinimumHeight(40)
        self.test_button.setEnabled(False)
        self.test_button.clicked.connect(self.test_api)
        button_layout.addWidget(self.test_button)
        
        server_layout.addLayout(button_layout)
        layout.addWidget(server_group)
        
        # Log output
        log_group = QGroupBox("Server Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: monospace;
            font-size: 11px;
        """)
        log_layout.addWidget(self.log_text)
        
        clear_button = QPushButton("Clear Log")
        clear_button.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_button)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        return tab
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Browser settings
        browser_group = QGroupBox("Browser Settings")
        browser_layout = QVBoxLayout(browser_group)
        
        browser_row = QHBoxLayout()
        browser_row.addWidget(QLabel("Browser:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["Firefox", "Chrome", "Brave", "Edge", "Safari", "Auto-detect"])
        browser_row.addWidget(self.browser_combo)
        browser_row.addStretch()
        browser_layout.addLayout(browser_row)
        layout.addWidget(browser_group)
        
        # Proxy settings
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QVBoxLayout(proxy_group)
        
        proxy_row = QHBoxLayout()
        proxy_row.addWidget(QLabel("HTTP Proxy:"))
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:2334 (optional)")
        proxy_row.addWidget(self.proxy_input)
        proxy_layout.addLayout(proxy_row)
        layout.addWidget(proxy_group)
        
        # Model settings
        model_group = QGroupBox("AI Model")
        model_layout = QVBoxLayout(model_group)
        
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("Default Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.0-pro"])
        model_row.addWidget(self.model_combo)
        model_row.addStretch()
        model_layout.addLayout(model_row)
        layout.addWidget(model_group)
        
        # Save button
        save_button = QPushButton("Save Settings")
        save_button.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        layout.addStretch()
        
        return tab
    
    def create_chat_tab(self) -> QWidget:
        """Create the test chat tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.setEnabled(False)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        layout.addWidget(self.chat_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("send_button")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_chat_message)
        layout.addWidget(self.send_button)
        
        # Response label
        layout.addWidget(QLabel("Response:"))
        
        # Response text
        self.chat_response = QTextEdit()
        self.chat_response.setReadOnly(True)
        self.chat_response.setStyleSheet("background-color: #2d2d2d;")
        layout.addWidget(self.chat_response)
        
        return tab
    
    def setup_tray(self):
        """Set up system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("WebAI-to-API")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.activateWindow()
    
    def start_server(self):
        """Start the Python backend server"""
        if self.server_running:
            return
        
        port = self.port_input.text() or "6969"
        self.log(f"Starting server on port {port}...")
        
        # Start server in thread
        self.server_thread = ServerThread(port=port)
        self.server_thread.output_signal.connect(self.handle_server_output)
        self.server_thread.finished_signal.connect(self.server_finished)
        self.server_thread.start()
        
        self.server_running = True
        self.update_server_status(True)
    
    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            return
        
        self.log("Stopping server...")
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread = None
        
        self.server_running = False
        self.update_server_status(False)
    
    def handle_server_output(self, output: str):
        """Handle server output"""
        self.log(output)
        
        # Check if server is ready
        if "Uvicorn running on" in output or "Application startup complete" in output:
            self.log("Server is ready!")
            self.update_server_status(True)
    
    def server_finished(self, exit_code: int):
        """Handle server process finish"""
        self.log(f"Server process finished with code {exit_code}")
        self.server_running = False
        self.update_server_status(False)
    
    def update_server_status(self, is_running: bool):
        """Update server status display"""
        self.server_running = is_running
        
        if is_running:
            self.server_status_label.setText("Server: Running")
            self.server_status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.start_button.setText("Stop Server")
            self.start_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px; border: none;")
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.stop_server)
            self.test_button.setEnabled(True)
            self.chat_input.setEnabled(True)
            self.send_button.setEnabled(True)
        else:
            self.server_status_label.setText("Server: Stopped")
            self.server_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            self.start_button.setText("Start Server")
            self.start_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border: none;")
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.start_server)
            self.test_button.setEnabled(False)
            self.chat_input.setEnabled(False)
            self.send_button.setEnabled(False)
    
    def check_server_status(self):
        """Check if server is responding"""
        if not self.server_running:
            return
        
        try:
            response = requests.get("http://localhost:6969/", timeout=2)
            if response.status_code == 200:
                self.status_label.setText("Status: Server responding")
            else:
                self.status_label.setText(f"Status: Server error {response.status_code}")
        except:
            self.status_label.setText("Status: Server not responding")
    
    def test_api(self):
        """Test the API endpoint"""
        self.log("Testing API...")
        
        # Test models endpoint
        try:
            response = requests.get("http://localhost:6969/v1/models", timeout=5)
            self.log(f"Models endpoint: {response.status_code}")
            
            # Try chat endpoint
            self.test_chat()
        except Exception as e:
            self.log(f"API test failed: {e}")
    
    def test_chat(self):
        """Test the chat endpoint"""
        try:
            response = requests.post(
                "http://localhost:6969/v1/chat/completions",
                json={
                    "model": "gemini-2.5-flash",
                    "messages": [{"role": "user", "content": "Hello!"}]
                },
                timeout=30
            )
            self.log(f"Chat endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    self.log(f"Response: {content[:100]}...")
        except Exception as e:
            self.log(f"Chat test failed: {e}")
    
    def send_chat_message(self):
        """Send a chat message"""
        if not self.server_running:
            return
        
        message = self.chat_input.text().strip()
        if not message:
            return
        
        self.log(f"Sending: {message}")
        self.chat_input.clear()
        
        # Get selected model
        model = self.model_combo.currentText()
        
        # Send request in thread to avoid blocking UI
        def make_request():
            try:
                response = requests.post(
                    "http://localhost:6969/v1/chat/completions",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": message}]
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        self.chat_response.append(f"You: {message}")
                        self.chat_response.append(f"AI: {content}")
                    else:
                        self.chat_response.append(f"Response: {data}")
                else:
                    self.chat_response.append(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                self.chat_response.append(f"Error: {e}")
        
        thread = threading.Thread(target=make_request, daemon=True)
        thread.start()
    
    def save_settings(self):
        """Save settings"""
        # In a full implementation, this would save to config file
        self.log("Settings saved!")
        QMessageBox.information(self, "Settings", "Settings saved! Restart server for changes to take effect.")
    
    def log(self, message: str):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Handle window close"""
        if self.server_running:
            self.stop_server()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("WebAI-to-API")
    app.setOrganizationName("WebAI")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

