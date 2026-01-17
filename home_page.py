from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QPushButton, QLabel, QGraphicsScene, 
                             QGraphicsView, QGraphicsPixmapItem, 
                             QVBoxLayout, QFrame, QHBoxLayout, 
                             QSizePolicy, QDialog, QGridLayout, 
                             QLineEdit, QCheckBox, QScrollArea,
                             QLayout,)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
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
        #self.setMaximumSize(1920, 1080)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.setSpacing(0)

        # No longer Fake Hopefully
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(20, -100, 1080, 520)

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
        self.refresh_view(self.game_data)

    def update_game_data(self, data):
        self.game_data = data

    def setup_side_panel(self):
        '''Create Side Panel'''
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(300)
        self.side_panel.setStyleSheet('background-color: rgba(100, 100, 100, 220); border-left: 2px solid #555;')

        layout = QVBoxLayout(self.side_panel)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.card_container = QWidget()
        self.card_container.setStyleSheet("background: transparent;")
        
        self.card_container_layout = QVBoxLayout(self.card_container)
        self.card_container_layout.setSpacing(5)
        self.card_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        task_entry_nav = QPushButton('Add Task')
        task_entry_nav.setCursor(Qt.CursorShape.PointingHandCursor)
        task_entry_nav.setFixedSize(300, 30)
        task_entry_nav.setStyleSheet('background-color: #555; color: white; border-radius: 5px;')
        task_entry_nav.clicked.connect(self.request_task_entry.emit)

        self.scroll_area.setWidget(self.card_container)
        layout.addWidget(self.scroll_area)

        layout.addWidget(task_entry_nav)        
    
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
        y = self.camera.height() - self.camera.bottom_btn.height()
        self.camera.bottom_btn.move(0, y)

        x_side = self.camera.width() - self.camera.side_btn.width()
        self.camera.side_btn.move(x_side, 0)

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

class UserTaskCard(QFrame):
    update_task_status_database = pyqtSignal(int, int)
    delete_request = pyqtSignal(int)

    def __init__(self, user_task):
        super().__init__()
        self.setObjectName("Card") 
        self.setFixedSize(280, 60)
        
        self.taskid = user_task.taskid

        self.setStyleSheet("""
            #Card {
                background-color: #444; 
                color: white; 
                border: 1px solid #666; 
                border-radius: 4px;
            }

            /* --- Checkbox Styling --- */
            QCheckBox {
                spacing: 8px; 
                font-size: 14px; 
                color: white;
                background: transparent;
                border: none;
                margin-left: 5px; 
            }
            QCheckBox::indicator {
                width: 18px;   
                height: 18px;
                border: 2px solid #ccc; 
                border-radius: 4px;
                background: #333; 
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }

            /* --- Labels (Metadata) --- */
            QLabel {
                color: #AAA; 
                font-size: 9px; 
                background: transparent;
                border: none;
                padding: 0px; margin: 0px; 
            }

            /* --- Action Button --- */
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                /* Optional: Since it's now floating, you might want all corners rounded? 
                   I kept your original right-side rounding for now. */
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                /* If you want it fully rounded like a pill, uncomment this:
                border-radius: 4px; 
                */
                font-weight: bold;
            }
            QPushButton:hover { background-color: #666; }
        """)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 2, 5, 2)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1) 
        layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("padding-right: 5px;")
        layout.addWidget(self.reward_label, 0, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

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

        self.delete_btn = QPushButton("✘")
        self.delete_btn.setFixedWidth(25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 20px; border: none;')
        layout.addWidget(self.delete_btn, 0, 2, 3, 1)

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
        
        self.taskid = user_task.taskid

        self.full_task_status = user_task.status

        self.setStyleSheet("""
            #Card {
                background-color: #444; 
                color: white; 
                border: 1px solid #666; 
                border-radius: 4px;
            }

            /* --- Checkbox Styling --- */
            QCheckBox {
                spacing: 8px; 
                font-size: 12px; 
                color: white;
                background: transparent;
                border: none;
                margin-left: 5px; 
            }
            QCheckBox::indicator {
                width: 15px;   
                height: 15px;
                border: 2px solid #ccc; 
                border-radius: 4px;
                background: #333; 
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }

            /* --- Labels (Metadata) --- */
            QLabel {
                color: #AAA; 
                font-size: 9px; 
                background: transparent;
                border: none;
                padding: 0px; margin: 0px; 
            }

            /* --- Action Button --- */
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                /* Optional: Since it's now floating, you might want all corners rounded? 
                   I kept your original right-side rounding for now. */
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                /* If you want it fully rounded like a pill, uncomment this:
                border-radius: 4px; 
                */
                font-weight: bold;
            }
            QPushButton:hover { background-color: #666; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        main_card_container = QWidget()
        main_card_container.setFixedSize(280, 60)
        main_card_layout = QGridLayout(main_card_container)
        main_card_layout.setSpacing(0)
        main_card_layout.setContentsMargins(5, 2, 5, 2)

        main_card_layout.setRowStretch(0, 0)
        main_card_layout.setRowStretch(1, 1) 
        main_card_layout.setRowStretch(2, 0)

        self.reward_label = QLabel(f"${user_task.reward}")
        self.reward_label.setStyleSheet("padding-right: 5px;")
        main_card_layout.addWidget(self.reward_label, 0, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        self.center_container = QWidget()
        self.center_container_layout = QHBoxLayout(self.center_container)
        self.center_container_layout.setSpacing(5)
        self.center_container_layout.setContentsMargins(5, 0, 0, 0)
        
        self.menu_btn = QPushButton(">")
        self.menu_btn.setFixedSize(18, 18)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.toggle_subtask_container)

        self.center_label = QLabel(f'{user_task.name}')
        self.center_label.setStyleSheet('spacing: 8px; font-size: 14px; color: white; background: transparent; border: none;')

        self.center_container_layout.addWidget(self.menu_btn)
        self.center_container_layout.addWidget(self.center_label)
        main_card_layout.addWidget(self.center_container, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self.time_due_label = QLabel(f"{user_task.time_due}" if user_task.deadline != 0 else "")
        self.time_due_label.setStyleSheet("padding-left: 2px;") 
        main_card_layout.addWidget(self.time_due_label, 2, 0, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        self.date_due_label = QLabel(f"{user_task.date_due}" if user_task.deadline != 0 else "")
        self.date_due_label.setStyleSheet("padding-right: 5px;")
        main_card_layout.addWidget(self.date_due_label, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        self.delete_btn = QPushButton("✘")
        self.delete_btn.setFixedWidth(25)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.delete_btn.setStyleSheet('background-color: transparent; color: #ff6666; font-size: 20px; border: none;')
        main_card_layout.addWidget(self.delete_btn, 0, 2, 3, 1)

        self.delete_btn.clicked.connect(lambda: self.delete_request.emit(self.taskid))

        main_card_layout.setColumnStretch(0, 1) 
        main_card_layout.setColumnStretch(1, 0) 
        main_card_layout.setColumnStretch(2, 0)

        self.subtasks_container = QWidget()
        self.subtasks_container_layout = QVBoxLayout(self.subtasks_container)
        self.subtasks_container_layout.setSpacing(5)
        self.subtasks_container_layout.setContentsMargins(20, 0, 5, 5)
        self.add_checkbox_list(user_task.subtasks)

        self.subtasks_container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        layout.addWidget(main_card_container)
        layout.addWidget(self.subtasks_container)
        self.subtasks_container.hide()
        layout.addStretch()

    def add_checkbox_list(self, subtask_list):
        for subtask in subtask_list:
            checkbox = QCheckBox(f'{subtask['name']}')
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
            self.menu_btn.setText('>')
            self.subtasks_container.hide()
        else:
            self.menu_btn.setText('v')
            self.subtasks_container.show()

    # def task_status_updated(self, checked):
    #     self.update_task_status_database.emit(int(checked), self.taskid)
    #     font = self.checkbox.font()
    #     font.setStrikeOut(checked)
    #     self.checkbox.setFont(font)

