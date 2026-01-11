import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from store_utils import UniversalStyles
from clothing_store import ClothingView
from furniture_store import FurnitureView

class MainShopsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikiT Stores")
        self.resize(1100, 750)

        #Initialize Theme
        self.styles = UniversalStyles(
            primary="#f8f8f8",
            secondary="#ffffff",
            border="#000000",
            hover="#a9a9a9",
            text="#000000",
            scroll="#888888",
            scroll_hover="#555555"
        )
        self.setStyleSheet(f"background-color: {self.styles.col_primary};")

        # User starting data
        self.data ={
            'money': 1000,
            'inventory_clothes': [],
            'worn_clothes': [],
            'equipped_clothes': [],
            'inventory_furniture': [],
            'placed_furniture': []
        }

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.view_furniture = FurnitureView(self, self.styles)
        self.view_clothing = ClothingView(self, self.styles)

        self.stack.addWidget(self.view_furniture) #0
        self.stack.addWidget(self.view_clothing) #1

        # Connect navigation signals
        self.view_furniture.request_clothing_view.connect(lambda: self.switch_view(1))
        self.view_furniture.request_home_view.connect(lambda: self.switch_view(0))
        self.view_clothing.request_furniture_view.connect(lambda: self.switch_view(0))
        self.view_clothing.request_home_view.connect(lambda: self.switch_view(0))

        # Connect money change signals
        self.view_furniture.money_changed.connect(self.sync_money)
        self.view_clothing.money_changed.connect(self.sync_money)

        #initial money display
        self.sync_money()

    def switch_view(self, index):
        """Switches between furniture and clothing views"""
        if index == 0:
            self.view_furniture.refresh_page() 
        elif index == 1:
            self.view_clothing.refresh_page() 
        self.stack.setCurrentIndex(index)

    def sync_money(self):
        """Makes money same throughout views"""
        self.view_clothing.refresh_page() 
        self.view_furniture.refresh_page() 

### EXECUTION FINALLYYY ######
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainShopsWindow()
    w.show()
    sys.exit(app.exec())