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
from home_page import RoomScene, UserTaskCard
from login_page import LoginPage
from data_manager import *
from store_utils import UniversalStyles
from clothing_store import ClothingView
from furniture_store import FurnitureView
from task_page import TaskEntryWidget
from task_handler import TaskDataHandler

uuid = None
db = DatabaseManager()
user_man = UserManager(db)
task_handler = TaskDataHandler()

def main():
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle('Tikkit - Login')
            self.setMinimumSize(1280, 720)
            self.setMaximumSize(1920, 1080)
            
            # Initialize user data structure
            self.data = {
                'money': 1000,
                'inventory_clothes': [],
                'worn_clothes': [],
                'equipped_clothes': [],
                'inventory_furniture': [],
                'placed_furniture': []
            }
            
            # Initialize Theme
            self.styles = UniversalStyles(
                primary="#f8f8f8",
                secondary="#ffffff",
                border="#000000",
                hover="#a9a9a9",
                text="#000000",
                scroll="#888888",
                scroll_hover="#555555"
            )
            
            # Create pages
            self.login_page = LoginPage()
            self.home_page = RoomScene()
            self.clothing_view = ClothingView(self, self.styles)
            self.furniture_view = FurnitureView(self, self.styles)
            self.task_entry = TaskEntryWidget()
            
            # stack with all pages
            self.pages = QStackedWidget()
            self.pages.addWidget(self.login_page)      # Index 0
            self.pages.addWidget(self.home_page)       # Index 1
            self.pages.addWidget(self.furniture_view)  # Index 2
            self.pages.addWidget(self.clothing_view)   # Index 3
            self.pages.addWidget(self.task_entry)      # Index 4
            
            # Connect login/logout signals
            self.login_page.login_success.connect(self.login)
            self.home_page.logout_signal.connect(self.logout)
            
            # Connect from home to store
            self.home_page.request_clothing_store.connect(self.switch_to_clothing)
            self.home_page.request_furniture_store.connect(self.switch_to_furniture)

            # from home to task entry
            self.home_page.request_task_entry.connect(self.switch_to_task_entry)
            
            # from clothing to home and furniture
            self.clothing_view.request_home_view.connect(self.switch_to_home)
            self.clothing_view.request_furniture_view.connect(self.switch_to_furniture)
            self.clothing_view.money_changed.connect(self.sync_money)
            
            # from furniture to home and clothing
            self.furniture_view.request_home_view.connect(self.switch_to_home)
            self.furniture_view.request_clothing_view.connect(self.switch_to_clothing)
            self.furniture_view.money_changed.connect(self.sync_money)

            # from task entry to home
            self.task_entry.request_main_page.connect(self.switch_to_home)
            
            # link task manager and task entry page
            self.task_entry.task_ready_signal.connect(task_handler.task_insertion)

            self.home_page.request_task_status_update.connect(task_handler.task_update_status)
            self.home_page.request_task_removal.connect(self.remove_and_update_tasks)
            
            self.setCentralWidget(self.pages)
            
            # Initial money display
            self.sync_money()
        
        def login(self, current_uuid):
            global uuid
            uuid = current_uuid
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.pages.setCurrentIndex(1)
        
        def switch_to_home(self):
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.pages.setCurrentIndex(1)
        
        def switch_to_clothing(self):
            self.setWindowTitle('Tikkit - Clothing Store')
            self.clothing_view.refresh_page()
            self.pages.setCurrentIndex(3)
        
        def switch_to_furniture(self):
            self.setWindowTitle('Tikkit - Furniture Store')
            self.furniture_view.refresh_page()
            self.pages.setCurrentIndex(2)
        
        def switch_to_task_entry(self):
            global uuid
            self.task_entry.update_uuid(uuid)
            self.setWindowTitle('Tikkit - Add Task')
            self.pages.setCurrentIndex(4)
        
        def sync_money(self):
            """Makes money same throughout views"""
            self.clothing_view.refresh_page() 
            self.furniture_view.refresh_page()
            # we need to do for the home page too

        def remove_and_update_tasks(self, taskid):
            task_handler.task_deletion(taskid)
            self.update_tasks()
            

        def update_tasks(self):
            global uuid
            user_task_list = task_handler.query_user_tasks(uuid)
            self.home_page.update_task_panel(user_task_list)
        
        def logout(self):
            self.setWindowTitle('Tikkit - Login')
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