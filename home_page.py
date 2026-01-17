from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit, QCheckBox, QScrollArea,
                             QLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from store_utils import default_theme
import sys
import os

class RoomScene(QWidget):

    logout_signal = pyqtSignal()
    request_clothing_store = pyqtSignal()
    request_furniture_store = pyqtSignal()
    request_task_entry = pyqtSignal()
    request_task_status_update = pyqtSignal(int, int)
    request_subtask_status_update = pyqtSignal(object, int, int, int)
    request_task_removal = pyqtSignal(int)

    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.setMinimumSize(1280, 720)
        self.styles = default_theme

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(20, -100, 1080, 520)

        # The Camera View
        self.camera = Camera(self.scene, self.styles)
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
        self.refresh_view(self.game_data)

    def update_game_data(self, data):
        self.game_data = data

    def setup_side_panel(self):
        '''Create Side Panel'''
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(300)
        self.side_panel.setStyleSheet(self.styles.panel_style())
       
        layout = QVBoxLayout(self.side_panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 15, 10, 15)

        lbl = QLabel('TASKS')
        lbl.setStyleSheet(f"font-weight: 900; font-size: 18px; color: {self.styles.col_text}; border: none;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl) 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(self.styles.scrollbar_style())

        self.card_container = QWidget()
        self.card_container.setStyleSheet("background: transparent;")
        
        self.card_container_layout = QVBoxLayout(self.card_container)
        self.card_container_layout.setSpacing(10)
        self.card_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        task_entry_nav = QPushButton('Add Task')
        task_entry_nav.setCursor(Qt.CursorShape.PointingHandCursor)
        task_entry_nav.setFixedSize(280, 40)
        task_entry_nav.setStyleSheet(self.styles.action_button_style())
        task_entry_nav.clicked.connect(self.request_task_entry.emit)

        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area)

        layout.addWidget(task_entry_nav, 0, Qt.AlignmentFlag.AlignHCenter)        
    
    def setup_bottom_panel(self):
        '''Create Bottom Panel'''
        self.bottom_panel = QFrame()
        self.bottom_panel.setFixedHeight(70)
        self.bottom_panel.setStyleSheet(self.styles.panel_style())

        layout = QHBoxLayout(self.bottom_panel)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 10, 20, 10)

        btn1 = QPushButton('Clothing Store')
        btn1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn1.setStyleSheet(self.styles.button_style())
        btn1.clicked.connect(self.request_clothing_store.emit)

        btn2 = QPushButton('Furniture Store')
        btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn2.setStyleSheet(self.styles.button_style())
        btn2.clicked.connect(self.request_furniture_store.emit)

        layout.addWidget(btn1)
        layout.addWidget(btn2)
    
    def setup_settings(self):
        '''Create settings pop-up'''
        settings = QDialog(self)
        settings.setWindowTitle('System Settings')
        settings.setFixedSize(300, 200)
        settings.setStyleSheet(f"background: {self.styles.col_secondary}; border: 2px solid {self.styles.col_border};")
        
        layout = QVBoxLayout(settings)
        layout.setSpacing(5)
        layout.setContentsMargins(20, 20, 20, 20)
        
        logout_btn = QPushButton('Logout ➜')
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        logout_btn.setFixedHeight(50)
        logout_btn.setStyleSheet(self.styles.action_button_style())
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

    def update_task_panel(self, user_task_list):
        while self.card_container_layout.count():
            item = self.card_container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        card_list = []
        for i in range(len(user_task_list)):
            if user_task_list[i].subdivisions != 0:
                card = UserDivTaskCard(user_task_list[i])
                card.update_task_status_database.connect(self.request_task_status_update.emit)
                card.update_subtask_status_database.connect(
                    lambda status, subtask_id, taskid, c=card: 
                    self.request_subtask_status_update.emit(c, status, subtask_id, taskid)
                )
                card.delete_request.connect(self.request_task_removal.emit)
                card_list.append(card)
            else:
                card = UserTaskCard(user_task_list[i])
                card.update_task_status_database.connect(self.request_task_status_update.emit)
                card.delete_request.connect(self.request_task_removal.emit)
                card_list.append(card)

        for card in card_list:
            self.card_container_layout.addWidget(card)

    def update_divtask_label(self, card, status):
        card.update_center_label(status)
    
    def update_button_positions(self):
        '''Adjust button postions'''
        y_bot = self.camera.height() - self.camera.bottom_btn.height()
        x_bot = (self.camera.width() - self.camera.bottom_btn.width()) // 2
        self.camera.bottom_btn.move(x_bot, y_bot - 5) 
        x_side = self.camera.width() - self.camera.side_btn.width()
        y_center = (self.camera.height() - self.camera.side_btn.height()) // 2
        self.camera.side_btn.move(x_side, y_center)
        margin = 10
        self.camera.settings_btn.move(margin, margin)
        
        money_x = self.camera.width() - self.camera.money_indicator.width() - margin
        self.camera.money_indicator.move(money_x, margin)

    def logout(self):
        '''Signal logout for page change'''
        self.logout_signal.emit()

    def refresh_view(self, data):
        self.camera.update_money(self.game_data.money)
        self.update_game_data(data)
        self.scene.clear()
        self.load_furniture()

    def get_image_path(self, item_name):
        assets_folder = 'assets'
        paths = []
        if not os.path.exists(assets_folder): return []
        
        for filename in os.listdir(assets_folder):
           if item_name.lower() in filename.lower() and filename.endswith('.png'):
                paths.append(os.path.join(assets_folder, filename))
        paths.sort()
        return paths
    
    def load_furniture(self):
        scale_factor = 0.8

        for item in self.game_data.placed_furniture:
            paths = self.get_image_path(item['name'])
            if not paths: continue

            angle_idx = item.get('angle_index', 0)
            if angle_idx >= len(paths): angle_idx = 0
            path = paths[angle_idx]
            
            if path and os.path.exists(path):
                
                pix = QPixmap(path)

                new_w = int(pix.width() * scale_factor)
                new_h = int(pix.height() * scale_factor)
                scaled_pix = pix.scaled(
                    new_w, new_h, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )

                pix_item = QGraphicsPixmapItem(scaled_pix)
                pix_item.setPos(item['x'], item['y'])
                pix_item.setZValue(item.get('z', 0))
                self.scene.addItem(pix_item)

                

class Camera(QGraphicsView):
    req_settings = pyqtSignal()
    def __init__(self, scene, styles):
        super().__init__(scene)
        self.styles = styles
        self.margin = 10

        self.bottom_btn = QPushButton('─', self)
        self.bottom_btn.setFixedSize(60, 20) 
        self.bottom_btn.setStyleSheet(self.styles.bottom_button_style())
        self.bottom_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.side_btn = QPushButton('〡', self)
        self.side_btn.setFixedSize(20, 60)
        self.side_btn.setStyleSheet(self.styles.side_button_style())
        self.side_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.settings_btn = QPushButton('⏣', self)
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setStyleSheet(self.styles.settings_button_style())
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.req_settings.emit)

        self.money_indicator = QLabel('$0', self)
        self.money_indicator.setStyleSheet(self.styles.money_label_style())

        self.update_button_positions()
        self.settings_btn.move(self.margin, self.margin)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        self.money_indicator.move(self.settings_btn.width()+self.margin, self.margin)

    def update_money(self, amount):
        '''Update money display'''
        self.money_indicator.setText(f'${amount}')
        self.money_indicator.adjustSize()
        self.update_button_positions()
        

    def resizeEvent(self, event):
        '''Adjust button postions upon resize'''
        super().resizeEvent(event)
        self.update_button_positions()

    def update_button_positions(self):
       margin = 10
       y_bot = self.height() - self.bottom_btn.height()
       self.bottom_btn.move((self.width() - self.bottom_btn.width()) // 2, y_bot)
       x_side = self.width() - self.side_btn.width()
       self.side_btn.move(x_side, (self.height() - self.side_btn.height()) // 2)
       self.settings_btn.move(margin, margin)
       money_x = self.width() - self.money_indicator.width() - margin
       self.money_indicator.move(money_x, margin) 
    
    def mousePressEvent(self, event):
        '''make it a pointer not hand'''
        super().mousePressEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        '''make it arrow not hand'''
        super().mouseReleaseEvent(event)
        self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

class UserTaskCard(QFrame):
    update_task_status_database = pyqtSignal(int, int)
    delete_request = pyqtSignal(int)

    def __init__(self, user_task):
        super().__init__()
        self.setObjectName("Card") 
        self.setFixedSize(255, 65) 
        self.styles = default_theme
        
        self.taskid = user_task.taskid

        self.setStyleSheet(self.styles.task_style())

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 2, 5, 2)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1) 
        layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.reward_label, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.checkbox = QCheckBox(f'{user_task.name}')
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setChecked(True if user_task.status == 1 else False)
        font = self.checkbox.font()
        font.setStrikeOut(self.checkbox.isChecked())
        self.checkbox.setFont(font)
        layout.addWidget(self.checkbox, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.checkbox.toggled.connect(self.task_status_updated)

        self.time_due_label = QLabel(f"{user_task.time_due}" if user_task.deadline != 0 else "")
        self.time_due_label.setStyleSheet("padding-left: 2px;") 
        layout.addWidget(self.time_due_label, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.date_due_label = QLabel(f"{user_task.date_due}" if user_task.deadline != 0 else "")
        self.date_due_label.setStyleSheet("padding-right: 5px;")
        layout.addWidget(self.date_due_label, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(25, 25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 18px; border: none; font-weight: 900;')
        layout.addWidget(self.delete_btn, 1, 2,  alignment=Qt.AlignmentFlag.AlignCenter)

        self.delete_btn.clicked.connect(lambda: self.delete_request.emit(self.taskid))

        layout.setColumnStretch(0, 1) 
        layout.setColumnStretch(1, 0) 
        layout.setColumnStretch(2, 0)

    def task_status_updated(self, checked):
        self.update_task_status_database.emit(int(checked), self.taskid)
        font = self.checkbox.font()
        font.setStrikeOut(checked)
        self.checkbox.setFont(font)

class UserDivTaskCard(QFrame):
    update_task_status_database = pyqtSignal(int, int)
    update_subtask_status_database = pyqtSignal(int, int, int)
    delete_request = pyqtSignal(int)

    def __init__(self, user_task):
        super().__init__()
        self.setObjectName("Card") 
        self.setFixedWidth(280)
        self.styles = default_theme
        
        self.taskid = user_task.taskid
        self.full_task_status = user_task.status

        self.setStyleSheet(self.styles.task_style())

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        main_card_container = QWidget()
        main_card_container.setFixedSize(250, 65)
        main_card_layout = QGridLayout(main_card_container)
        main_card_layout.setSpacing(0)
        main_card_layout.setContentsMargins(5, 2, 5, 2)

        main_card_layout.setRowStretch(0, 0)
        main_card_layout.setRowStretch(1, 1) 
        main_card_layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("padding-right: 5px; font-weight: bold;")
        main_card_layout.addWidget(self.reward_label, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.center_container = QWidget()
        self.center_container_layout = QHBoxLayout(self.center_container)
        self.center_container_layout.setSpacing(5)
        self.center_container_layout.setContentsMargins(5, 0, 0, 0)
        
        self.menu_btn = QPushButton("►")
        self.menu_btn.setFixedSize(18, 18)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_subtask_container)

        self.center_label = QLabel(f'{user_task.name}')
        self.center_label.setStyleSheet('spacing: 8px; font-size: 14px; background: transparent; border: none; font-weight: bold;')
        font = self.center_label.font()
        font.setStrikeOut(bool(user_task.status))
        self.center_label.setFont(font)

        self.center_container_layout.addWidget(self.menu_btn)
        self.center_container_layout.addWidget(self.center_label)
        main_card_layout.addWidget(self.center_container, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.time_due_label = QLabel(f"{user_task.time_due}" if user_task.deadline != 0 else "")
        self.time_due_label.setStyleSheet("padding-left: 2px;") 
        main_card_layout.addWidget(self.time_due_label, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.date_due_label = QLabel(f"{user_task.date_due}" if user_task.deadline != 0 else "")
        self.date_due_label.setStyleSheet("padding-right: 5px;")
        main_card_layout.addWidget(self.date_due_label, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedWidth(25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 18px; border: none; font-weight: 900;')
        main_card_layout.addWidget(self.delete_btn, 1, 2,  alignment=Qt.AlignmentFlag.AlignCenter)

        self.delete_btn.clicked.connect(lambda: self.delete_request.emit(self.taskid))

        main_card_layout.setColumnStretch(0, 1) 
        main_card_layout.setColumnStretch(1, 0) 
        main_card_layout.setColumnStretch(2, 0)

        self.subtasks_container = QWidget()
        self.subtasks_container.setStyleSheet(f"background: transparent; border: none {self.styles.col_border};")
        self.subtasks_container_layout = QVBoxLayout(self.subtasks_container)
        self.subtasks_container_layout.setSpacing(5)
        self.subtasks_container_layout.setContentsMargins(20, 0, 5, 10)
        self.add_checkbox_list(user_task.subtasks)

        self.subtasks_container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        layout.addWidget(main_card_container)
        layout.addWidget(self.subtasks_container)
        self.subtasks_container.hide()
        layout.addStretch()

    def add_checkbox_list(self, subtask_list):
        for subtask in subtask_list:
            checkbox = QCheckBox(f"{subtask['name']}")
            checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
            checkbox.setChecked(True if subtask['status'] == 1 else False)
            font = checkbox.font()
            font.setStrikeOut(checkbox.isChecked())
            checkbox.setFont(font)
            checkbox.toggled.connect(
                lambda checked, subtask_id=subtask['subtask_id'], chk = checkbox: 
                self.subtask_status_updated(checked, subtask_id, chk)
                )
            self.subtasks_container_layout.addWidget(checkbox)
        self.subtasks_container_layout.addStretch()

    def subtask_status_updated(self, checked, subtask_id, checkbox):
        self.update_subtask_status_database.emit(int(checked), subtask_id, self.taskid)
        font = checkbox.font()
        font.setStrikeOut(checked)
        checkbox.setFont(font)

    def update_center_label(self, status):
        font = self.center_label.font()
        font.setStrikeOut(bool(status))
        self.center_label.setFont(font)

    def toggle_subtask_container(self):
        if self.subtasks_container.isVisible():
            self.menu_btn.setText('►')
            self.subtasks_container.hide()
        else:
            self.menu_btn.setText('▼')
            self.subtasks_container.show()