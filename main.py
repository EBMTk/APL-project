from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QVBoxLayout, QFrame, QHBoxLayout, QSizePolicy, QDialog
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import sys

import home_page
import login_page

def main():
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle('Home')
            self.setMinimumSize(1280, 720)
            self.setMaximumSize(1920, 1080)

            self.room_scene = home_page.RoomScene()
            self.setCentralWidget(self.room_scene)

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()