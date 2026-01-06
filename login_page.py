from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit,)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1920, 1080)

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.login_card = QFrame()
        self.login_card.setFixedSize(300, 200)
        self.login_card.setStyleSheet("background-color: #333; border-radius: 8px;")

        self.button_container = QWidget()
        self.button_container.setFixedHeight(30)

        self.card_layout = QVBoxLayout(self.login_card)
        self.card_buttons_layout = QHBoxLayout(self.button_container)
        self.card_buttons_layout.setContentsMargins(0, 0, 0, 0)

        email_label = QLabel("Username")
        email_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFFFFF;")
        self.email_input = QLineEdit()

        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                background-color: #222;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #5865F2;
            }
        """)
        
        pass_label = QLabel("Password")
        pass_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #FFFFFF;")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.pass_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                background-color: #222;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #5865F2;
            }
        """)
        
        login_btn = QPushButton('Login')
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        login_btn.setStyleSheet('background-color: #555; color: white; border-radius: 4px;')

        signup_btn = QPushButton('Sign Up')
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        signup_btn.setStyleSheet('background-color: #555; color: white; border-radius: 4px;')

        self.card_buttons_layout.addWidget(login_btn)
        self.card_buttons_layout.addWidget(signup_btn)

        self.card_layout.addWidget(email_label)
        self.card_layout.addWidget(self.email_input)
        self.card_layout.addWidget(pass_label)
        self.card_layout.addWidget(self.pass_input)
        self.card_layout.addWidget(self.button_container)

        self.main_layout.addWidget(self.login_card, 0, 0, Qt.AlignmentFlag.AlignCenter)