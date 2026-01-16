from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit, QStackedWidget,)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

# Import your modules
import home_page
import login_page
from data_manager import *
from store_utils import GameData
from clothing_store import ClothingView
from furniture_store import FurnitureView

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

            self.game_data = GameData()
                      
            # Create pages
            self.login_page = login_page.LoginPage()
            self.home_page = home_page.RoomScene(self.game_data)
            self.clothing_view = ClothingView(self.game_data)
            self.furniture_view = FurnitureView(self.game_data)

            # stack with all pages
            self.pages = QStackedWidget()
            self.pages.addWidget(self.login_page)      # Index 0
            self.pages.addWidget(self.home_page)       # Index 1
            self.pages.addWidget(self.furniture_view)  # Index 2
            self.pages.addWidget(self.clothing_view)   # Index 3
            
            # Connect login/logout signals
            self.login_page.login_success.connect(self.switch_to_home)
            self.home_page.logout_signal.connect(self.logout)
            
            # Connect from home to store
            self.home_page.request_clothing_store.connect(self.switch_to_clothing)
            self.home_page.request_furniture_store.connect(self.switch_to_furniture)
            
            # from clothing to home and furniture
            self.clothing_view.request_home_view.connect(self.switch_to_home_from_store)
            self.clothing_view.request_furniture_view.connect(self.switch_to_furniture)
            self.clothing_view.money_changed.connect(self.sync_money)
            
            # from furniture to home and clothing
            self.furniture_view.request_home_view.connect(self.switch_to_home_from_store)
            self.furniture_view.request_clothing_view.connect(self.switch_to_clothing)
            self.furniture_view.money_changed.connect(self.sync_money)
            
            self.setCentralWidget(self.pages)
            
            # Initial money display
            self.sync_money()
        
        def switch_to_home(self, current_uuid):
            global uuid
            self.pages.setCurrentIndex(1)
            uuid = current_uuid
        
        def switch_to_home_from_store(self):
            self.home_page.refresh_view()
            self.pages.setCurrentIndex(1)
        
        def switch_to_clothing(self):
            self.clothing_view.refresh_page()
            self.pages.setCurrentIndex(3)
        
        def switch_to_furniture(self):
            self.furniture_view.refresh_page()
            self.pages.setCurrentIndex(2)
        
        def sync_money(self):
            """Makes money same throughout views"""
            self.clothing_view.refresh_page() 
            self.furniture_view.refresh_page()
            # we need to do for the home page too
        
        def logout(self):
            global uuid
            user_man.logout(uuid)
            self.pages.setCurrentIndex(0)
            uuid = None
        
        def closeEvent(self, event):
            global uuid
            if uuid:
                user_man.logout(uuid)
            return super().closeEvent(event)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()