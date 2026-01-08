from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit, QStackedWidget,)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

import home_page
import login_page
from data_manager import *

uuid = None
db = DatabaseManager()
user_man = UserManager(db)

def main():
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle('Tikkit')
            self.setMinimumSize(1280, 720)
            self.setMaximumSize(1920, 1080)

            self.login_page = login_page.LoginPage()
            self.home_page = home_page.RoomScene()

            self.pages = QStackedWidget()
            self.pages.addWidget(self.login_page)
            self.pages.addWidget(self.home_page)

            self.login_page.login_success.connect(self.switch_to_home)
            self.home_page.logout_signal.connect(self.logout)

            self.setCentralWidget(self.pages)

        def switch_to_home(self, current_uuid):
            global uuid
            self.pages.setCurrentIndex(1)
            uuid = current_uuid

        def logout(self):
            global uuid
            user_man.logout(uuid)
            self.pages.setCurrentIndex(0)
            uuid = None

        def closeEvent(self, event):
            global uuid
            user_man.logout(uuid)
            return super().closeEvent(event)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()