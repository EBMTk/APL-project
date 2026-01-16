from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit,)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys
import os

class RoomScene(QWidget):

    logout_signal = pyqtSignal()
    request_clothing_store = pyqtSignal()
    request_furniture_store = pyqtSignal()

    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1920, 1080)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

        # No longer Fake Hopefully
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 600, 600)

        #The Camera View
        self.camera = Camera(self.scene)
        self.camera.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.camera.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)   
        
        self.camera.bottom_btn.clicked.connect(self.toggle_bottom)
        self.camera.side_btn.clicked.connect(self.toggle_side)

        self.setup_bottom_panel()
        self.center_layout.addWidget(self.camera)
        self.center_layout.addWidget(self.bottom_panel)
        self.setup_side_panel()
        self.main_layout.addWidget(self.center_container)
        self.main_layout.addWidget(self.side_panel)

        self.camera.req_settings.connect(self.setup_settings)
        self.refresh_view()

    def setup_side_panel(self):
        '''Create Side Panel'''
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(300)
        self.side_panel.setStyleSheet('background-color: rgba(100, 100, 100, 220); border-left: 2px solid #555;')
    
    def setup_bottom_panel(self):
        '''Create Bottom Panel'''
        self.bottom_panel = QFrame()
        self.bottom_panel.setFixedHeight(50)
        self.bottom_panel.setStyleSheet('background-color: rgba(100, 100, 100, 220); border-left: 2px solid #555;')

        layout = QHBoxLayout(self.bottom_panel)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)

        btn1 = QPushButton('Open Clothing Store')
        btn1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn1.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')
        btn1.clicked.connect(self.request_clothing_store.emit)

        btn2 = QPushButton('Open Furniture Store')
        btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn2.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')
        btn2.clicked.connect(self.request_furniture_store.emit)

        layout.addWidget(btn1)
        layout.addWidget(btn2)
    
    def setup_settings(self):
        '''Create settings pop-up'''
        settings = QDialog(self)
        settings.setWindowTitle('System Settings')
        settings.setFixedSize(300, 200)
        
        layout = QVBoxLayout(settings)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        
        logout_btn = QPushButton('Logout ➜]')
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        logout_btn.setFixedHeight(50)
        logout_btn.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')
        logout_btn.clicked.connect(settings.accept)

        layout.addStretch()
        layout.addWidget(logout_btn)

        if settings.exec():
            self.logout()
    
    def toggle_bottom(self):
        '''Toggle bottom panel visability'''
        if self.bottom_panel.isVisible():
            self.bottom_panel.hide()
        else:
            self.bottom_panel.show()
    
    def toggle_side(self):
        '''Toggle bottom panel visability'''
        if self.side_panel.isVisible():
            self.side_panel.hide()
        else:
            self.side_panel.show()

    def resizeEvent(self, event):
        '''Adjust button postions upon resize'''
        super().resizeEvent(event)
        self.update_button_positions()
    
    def update_button_positions(self):
        '''Adjust button postions'''
        y = self.camera.height() - self.camera.bottom_btn.height()
        self.camera.bottom_btn.move(0, y)

        x_side = self.camera.width() - self.camera.side_btn.width()
        self.camera.side_btn.move(x_side, 0)

    def logout(self):
        '''Signal logout for page change'''
        self.logout_signal.emit()

    def refresh_view(self):
        self.camera.update_money(self.game_data.money)
        self.scene.clear()
        self.load_furniture()

    def get_image_path(self, item_name):
        assets_folder = 'assets'
        if not os.path.exists(assets_folder): return None
        for filename in os.listdir(assets_folder):
           if item_name.lower() in filename.lower() and filename.endswith('.png'):
                return os.path.join(assets_folder, filename)
        return None
    
    def load_furniture(self):
        for item in self.game_data.placed_furniture:
            path = self.get_image_path(item['name'])
            if path and os.path.exists(path):
                pix_item = QGraphicsPixmapItem(QPixmap(path).scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                pix_item.setPos(item['x'], item['y'])
                self.scene.addItem(pix_item)

               

class Camera(QGraphicsView):
    req_settings = pyqtSignal()
    def __init__(self, scene):
        super().__init__(scene)

        margin = 10

        self.bottom_btn = QPushButton('==', self)
        self.bottom_btn.setFixedSize(20, 10)
        self.bottom_btn.setStyleSheet('background-color: #444; color: white; border: none;')
        self.bottom_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.side_btn = QPushButton('||', self)
        self.side_btn.setFixedSize(10, 20)
        self.side_btn.setStyleSheet('background-color: #444; color: white; border: none;')
        self.side_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.settings_btn = QPushButton('⏣', self)
        self.settings_btn.setFixedSize(20, 20)
        self.settings_btn.setStyleSheet('background-color: #444; color: white; border: none;')
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.req_settings.emit)

        self.money_indicator = QLabel('$0', self)
        self.money_indicator.setStyleSheet('''
            color: white; 
            font-size: 12px; 
            background-color: rgba(0, 0, 0, 150);
            padding: 3px;
            border-radius: 4px;
        ''')
        self.money_indicator.move(self.settings_btn.width()+margin, margin)

        self.update_button_positions()
        self.settings_btn.move(margin, margin)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def update_money(self, amount):
        '''Update money display'''
        self.money_indicator.setText(f'${amount}')
        self.money_indicator.adjustSize()

    def resizeEvent(self, event):
        '''Adjust button postions upon resize'''
        super().resizeEvent(event)
        self.update_button_positions()

    def update_button_positions(self):
        '''Adjust button postions'''
        y_bot = self.height() - self.bottom_btn.height()
        self.bottom_btn.move(0, y_bot)

        x_side = self.width() - self.side_btn.width()
        self.side_btn.move(x_side, 0)

    #this part just to make the cursor not a hand when dragging
    def mousePressEvent(self, event):
        '''make it a pointer not hand'''
        super().mousePressEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        '''make it arrow not hand'''
        super().mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)