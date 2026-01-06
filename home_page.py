from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QFrame, QHBoxLayout, QSizePolicy, QDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

class RoomScene(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1280, 720)
        self.setMaximumSize(1920, 1080)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

        # Fake scene, place holder
        self.pseudo_scene = QGraphicsScene()
        self.pseudo_scene.setSceneRect(-100, -100, 200, 200)
        # Object to make sure im not tweaking
        chair = QPixmap('chair.png')
        tweaker_chair = QGraphicsPixmapItem(chair)
        tweaker_chair.setOffset(-(chair.width())/2, -(chair.height())/2)
        tweaker_chair.setScale(0.5)
        self.pseudo_scene.addItem(tweaker_chair)
        
        self.camera = Camera(self.pseudo_scene)
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

        btn1 = QPushButton('WOH OMG ITS A SHOP')
        btn1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn1.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')

        btn2 = QPushButton('WOH OMG ITS- wait i already did this')
        btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn2.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')

        layout.addWidget(btn1)
        layout.addWidget(btn2)
    
    def setup_settings(self):
        settings = QDialog(self)
        settings.setWindowTitle("System Settings")
        settings.setFixedSize(300, 200)
        settings.exec()

        
    
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

        self.money_indicator = QLabel('$Balling Hard', self)
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