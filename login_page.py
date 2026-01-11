from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit, QStackedWidget, )
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

from data_manager import DatabaseManager, UserManager

db = DatabaseManager()
user_man = UserManager(db)

class LoginPage(QWidget):

    login_success = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1920, 1080)

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.center_card = QFrame()
        self.center_card.setFixedSize(300, 250)
        self.center_card.setStyleSheet('background-color: #333; border-radius: 8px;')

        self.bottom_card = QFrame()
        self.bottom_card.setFixedSize(300, 25)
        self.bottom_card.setStyleSheet('background-color: #333; border-radius: 8px;')

        self.pages = QStackedWidget()
        self.login_card = QWidget()
        self.signup_card = QWidget()

        self.pages.addWidget(self.login_card)
        self.pages.addWidget(self.signup_card)

        self.input_style = '''
            QLineEdit {
                border: 2px solid #555;
                border-radius: 4px;
                padding: 5px;
                background-color: #222;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #4a6741;
            }
        '''
        self.label_style = 'font-size: 12px; font-weight: bold; color: #FFFFFF;'
        self.error_label_style = 'font-size: 12px; color: #FF0000;'
        self.button_style = 'background-color: #555; color: white; border-radius: 4px;'

        self.center_card_layout = QVBoxLayout(self.center_card)
        self.center_card_layout.setContentsMargins(2, 2, 2, 2)
        self.center_card_layout.addWidget(self.pages)
        self.center_card_layout.addWidget(self.bottom_card)

        self.bottom_label = QLabel('Welcome back!')
        self.bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_label.setStyleSheet(self.label_style)

        self.bottom_card_layout = QVBoxLayout(self.bottom_card)
        self.bottom_card_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_card_layout.addWidget(self.bottom_label)
        

        self.setup_login_card()
        self.setup_signup_card()
        self.switch_to_login()

        self.main_layout.addWidget(self.center_card, 0, 0, Qt.AlignmentFlag.AlignCenter)

    def setup_login_card(self):
        self.login_card_layout = QVBoxLayout(self.login_card)
        self.login_card_layout.setContentsMargins(2, 2, 2, 2)
        self.login_card_layout.setSpacing(5)

        self.login_button_container = QWidget()
        self.login_button_container.setFixedHeight(30)

        self.login_buttons_layout = QHBoxLayout(self.login_button_container)
        self.login_buttons_layout.setContentsMargins(0, 0, 0, 0)

        user_label = QLabel('Username')
        user_label.setStyleSheet(self.label_style)
        self.login_user_input = QLineEdit()
        self.login_user_input.setStyleSheet(self.input_style)
        
        pass_label = QLabel('Password')
        pass_label.setStyleSheet(self.label_style)
        self.login_pass_input = QLineEdit()
        self.login_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_pass_input.setStyleSheet(self.input_style)

        login_btn = QPushButton('Login')
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        login_btn.setStyleSheet(self.button_style)
        login_btn.clicked.connect(self.login)

        signup_btn = QPushButton('Sign Up')
        signup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        signup_btn.setStyleSheet(self.button_style)
        signup_btn.clicked.connect(self.switch_to_signup)

        self.login_buttons_layout.addWidget(login_btn)
        self.login_buttons_layout.addWidget(signup_btn)

        self.login_card_layout.addWidget(user_label)
        self.login_card_layout.addWidget(self.login_user_input)
        self.login_card_layout.addWidget(pass_label)
        self.login_card_layout.addWidget(self.login_pass_input)
        self.login_card_layout.addSpacing(5)
        self.login_card_layout.addWidget(self.login_button_container)

    def setup_signup_card(self):
        self.signup_card_layout = QVBoxLayout(self.signup_card)
        self.signup_card_layout.setContentsMargins(2, 2, 2, 2)
        self.signup_card_layout.setSpacing(5)
        
        self.signup_button_container = QWidget()
        self.signup_button_container.setFixedHeight(30)

        self.signup_buttons_layout = QHBoxLayout(self.signup_button_container)
        self.signup_buttons_layout.setContentsMargins(0, 0, 0, 0)

        create_user_label = QLabel('Create Username')
        create_user_label.setStyleSheet(self.label_style)
        self.signup_user_input = QLineEdit()
        self.signup_user_input.setStyleSheet(self.input_style)
        
        create_pass_label = QLabel('Create Password')
        create_pass_label.setStyleSheet(self.label_style)
        self.signup_pass_input = QLineEdit()
        self.signup_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_pass_input.setStyleSheet(self.input_style)

        conf_pass_label = QLabel('Confirm Password')
        conf_pass_label.setStyleSheet(self.label_style)
        self.signup_conf_pass_input = QLineEdit()
        self.signup_conf_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_conf_pass_input.setStyleSheet(self.input_style)

        back_btn = QPushButton('Back')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        back_btn.setStyleSheet(self.button_style)
        back_btn.clicked.connect(self.switch_to_login)

        reg_btn = QPushButton('Register')
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        reg_btn.setStyleSheet(self.button_style)
        reg_btn.clicked.connect(self.signup)
        
        self.signup_buttons_layout.addWidget(back_btn)
        self.signup_buttons_layout.addWidget(reg_btn)

        self.signup_card_layout.addWidget(create_user_label)
        self.signup_card_layout.addWidget(self.signup_user_input)
        self.signup_card_layout.addWidget(create_pass_label)
        self.signup_card_layout.addWidget(self.signup_pass_input)
        self.signup_card_layout.addWidget(conf_pass_label)
        self.signup_card_layout.addWidget(self.signup_conf_pass_input)
        self.signup_card_layout.addSpacing(5)
        self.signup_card_layout.addWidget(self.signup_button_container)

    def switch_to_signup(self):
        self.bottom_label.setText('Glad you can join us!')
        self.bottom_label.setStyleSheet(self.label_style)
        self.center_card.setFixedHeight(275) 
        self.pages.setCurrentIndex(1)
    
    def switch_to_login(self):
        self.bottom_label.setText('Welcome back!')
        self.bottom_label.setStyleSheet(self.label_style)
        self.center_card.setFixedHeight(200) 
        self.pages.setCurrentIndex(0)

    def login(self):
        entered_username = self.login_user_input.text()
        entered_password = self.login_pass_input.text()

        status, message = user_man.validate_and_login(entered_username, entered_password)

        if status:
            self.clear_inputs()
            self.switch_to_login()
            self.login_success.emit(user_man.current_uuid)
        else:
            self.bottom_label.setText(message)
            self.bottom_label.setStyleSheet(self.error_label_style)
    
    def signup(self):
        entered_username = self.signup_user_input.text()
        entered_password = self.signup_pass_input.text()
        confirmed_password = self.signup_conf_pass_input.text()

        status, message = user_man.validate_and_register(entered_username, entered_password, confirmed_password)

        if status:
            self.clear_inputs()
            self.switch_to_login()
            self.login_success.emit(user_man.current_uuid)
        else:
            self.bottom_label.setText(message)
            self.bottom_label.setStyleSheet(self.error_label_style)

    def clear_inputs(self):
        self.signup_user_input.clear()
        self.signup_pass_input.clear()
        self.signup_conf_pass_input.clear()
        self.login_user_input.clear()
        self.login_pass_input.clear()