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
from home_page import RoomScene
from login_page import LoginPage
from data_manager import *
from store_utils import GameData
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

            self.game_data = GameData()
                      
            # Create pages
            self.login_page = LoginPage()
            self.home_page = RoomScene(self.game_data)
            self.clothing_view = ClothingView(self.game_data)
            self.furniture_view = FurnitureView(self.game_data)
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
            self.home_page.request_subtask_status_update.connect(self.update_divtask)
            self.home_page.request_task_removal.connect(self.remove_and_update_tasks)

            self.furniture_view.request_save_layout.connect(self.save_furniture_data)

            self.clothing_view.checkout_completed.connect(self.save_clothe_data)
            
            self.setCentralWidget(self.pages)
            
            # Initial money display
            
        
        def init_game_data(self, current_uuid):
            inv_furn_list, eqp_furn_list = user_man.retrieve_user_furniture_data(current_uuid)
            self.game_data.inventory_furniture = inv_furn_list
            self.game_data.placed_furniture = eqp_furn_list
            # self.game_money = query for mula
            self.furniture_view.load_layout(eqp_furn_list)
            self.sync_money()
            # self.clothing_view.update_clothes_data(data)
            pass

        def init_visuals(self):
            pass

        def save_furniture_data(self, inventory_furniture, placed_furniture):
            global uuid
            user_man.save_user_furniture_data(uuid, inventory_furniture, placed_furniture)

        def save_clothe_data(self, inventory_clothes, equipped_clothes):
            global uuid
            user_man.save_user_clothe_data(uuid, inventory_clothes, equipped_clothes)

        def update_game_data(self, data):
            global uuid
            # enter data back into database
        
        def login(self, current_uuid):
            global uuid
            uuid = current_uuid
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.init_game_data(current_uuid)
            self.home_page.refresh_view(self.game_data)
            self.pages.setCurrentIndex(1)
        
        def switch_to_home(self):
            self.update_tasks()
            self.setWindowTitle('Tikkit')
            self.home_page.refresh_view(self.game_data)
            self.pages.setCurrentIndex(1)
        
        def switch_to_clothing(self):
            self.setWindowTitle('Tikkit - Clothing Store')
            self.clothing_view.refresh_page()
            self.pages.setCurrentIndex(3)
        
        def switch_to_furniture(self):
            self.setWindowTitle('Tikkit - Furniture Store')
            self.furniture_view.refresh_page(self.game_data)
            self.pages.setCurrentIndex(2)
        
        def switch_to_task_entry(self):
            global uuid
            self.task_entry.update_uuid(uuid)
            self.setWindowTitle('Tikkit - Add Task')
            self.pages.setCurrentIndex(4)
        
        def sync_money(self):
            """Makes money same throughout views"""
            self.clothing_view.refresh_page() 
            self.furniture_view.refresh_page(self.game_data)
            # we need to do for the home page too

        def remove_and_update_tasks(self, taskid):
            task_handler.task_deletion(taskid)
            self.update_tasks()

        def update_tasks(self):
            global uuid
            user_task_list = task_handler.query_user_tasks(uuid)
            self.home_page.update_task_panel(user_task_list)

        def update_divtask(self, card, status, subtask_id, taskid):
            task_handler.subtask_update_status(status, subtask_id)
            divtask_status = task_handler.query_divtask_status(taskid)
            self.home_page.update_divtask_label(card, divtask_status)
        
        def logout(self):
            self.setWindowTitle('Tikkit - Login')
            global uuid
            user_man.logout(uuid)
            self.home_page.refresh_view(GameData())
            self.pages.setCurrentIndex(0)
            uuid = None
        
        def closeEvent(self, event):
            global uuid
            if uuid:
                user_man.logout(uuid)
                self.home_page.refresh_view(GameData())
            return super().closeEvent(event)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()