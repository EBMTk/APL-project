from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from store_utils import store_header

### CLOTHING_CARD ### 
class ClothingCard(QFrame):
    def __init__(self, name, price, parent_view, styles):
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles

        self.setFixedHeight(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f"""
                            QFrame {{
                                background-color: {self.styles.col_secondary};
                                border: 1.5px solid {self.styles.col_border};
                                border-radius: 15px;
                            }}
                            """)
        layout = QHBoxLayout(self)

        info_layout = QVBoxLayout()
        self.lbl_name = QLabel(name)
        self.lbl_price = QLabel(f"${price}")
        self.lbl_name.setStyleSheet(f"color: {self.styles.col_text}; font-size: 16px; font-weight: bold; border: none;")
        self.lbl_price.setStyleSheet(f"color: {self.styles.col_text}; font-size: 14px; border: none;")

        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_price)

        btn_layout = QVBoxLayout()

        self.btn_wear = QPushButton("Wear")
        self.btn_wear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_wear.setStyleSheet(f"""
        QPushButton {{
            background: {self.styles.col_secondary};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_text};
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        QPushButton:disabled {{ background: #cccccc; color: #888888; }}
        """)
        self.btn_wear.clicked.connect(self.try_item)

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f"""
        QPushButton {{
            background: {self.styles.col_border};
            color: {self.styles.col_primary};
            border:none;
            border-radius: 8px;
            font-weight: bold;
            padding: 4px;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        QPushButton:disabled {{ background: #cccccc; color: #888888; }}
        """)
        self.btn_buy.clicked.connect(self.buy_item)
        
        btn_layout.addWidget(self.btn_wear)
        btn_layout.addWidget(self.btn_buy)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout) 

        if self.name in self.parent_view.main_window.data['inventory_clothes']:
            self.set_owned_state()
        if self.name in self.parent_view.main_window.data['worn_clothes']:
            self.set_worn_state()

    def set_owned_state(self):
        self.btn_buy.setText("Owned")
        self.btn_buy.setDisabled(True)
        self.lbl_price.setText("In Inventory")
        
    def set_worn_state(self):
        self.btn_wear.setText("Take Off")
        self.btn_wear.setStyleSheet(f"""
        QPushButton {{
            background: {self.styles.col_text};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_secondary};
            font-weight: bold;
        }}
        QPushButton:hover {{ opacity: 0.9; }}
        """)

    def set_unworn_state(self):
        self.btn_wear.setText("Wear")
        self.btn_wear.setStyleSheet(f"""
        QPushButton {{
            background: {self.styles.col_secondary};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_text};
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        """)
    
    def buy_item(self):
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success: self.set_owned_state()
    
    def try_item(self):
        if self.btn_wear.text() == "Take Off":
            self.parent_view.unwear_item(self.name)
            self.set_unworn_state()
        else:
            self.parent_view.wear_item(self.name)
            self.set_worn_state()

### CLOTHING_VIEW ###
class ClothingView(QWidget):
    request_furniture_view = pyqtSignal()
    request_home_view = pyqtSignal()
    money_changed = pyqtSignal(int)

    def __init__(self, main_window, styles):
        super().__init__()
        self.main_window = main_window
        self.styles = styles

        self.clothing_items = [
            ("T-Shirt", 20), ("Jeans", 40), ("Jacket", 60), ("Sneakers", 50),
            ("Hat", 15), ("Sunglasses", 25), ("Dress", 70), ("Boots", 80),
        ]
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_container = QFrame()
        left_container.setStyleSheet(self.styles.frame_style())
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(20, 20, 20, 20)

        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.request_home_view.emit)

        title = QLabel("Clothing Shop")
        title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preview_area = QLabel("Try Item")
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setStyleSheet(f"background: transparent; border: none; color: {self.styles.col_text}; font-size: 18px;")
        
        self.btn_go_furniture = QPushButton("Browse Furniture")
        self.btn_go_furniture.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_furniture.setStyleSheet(self.styles.action_button_style())
        self.btn_go_furniture.clicked.connect(self.request_furniture_view.emit)
        self.btn_go_furniture.setFixedHeight(60)

        left_layout.addWidget(self.header)
        left_layout.addWidget(title)
        left_layout.addStretch()
        left_layout.addWidget(self.preview_area)
        left_layout.addStretch()
        left_layout.addWidget(self.btn_go_furniture)

        right_container = QFrame()
        right_container.setStyleSheet(self.styles.frame_style())
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 20, 20, 20)

        right_title = QLabel("Available Clothing")
        right_title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 22px; font-weight: bold; border: none;")
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.styles.scrollbar_style())

        item_container = QWidget()
        item_container.setStyleSheet("background: transparent; ")
        item_layout = QVBoxLayout(item_container)
        item_layout.setSpacing(10)

        for name, price in self.clothing_items:
            card = ClothingCard(name, price, self, self.styles)
            item_layout.addWidget(card)

        item_layout.addStretch() 
        scroll_area.setWidget(item_container)

        right_layout.addWidget(right_title)
        right_layout.addWidget(scroll_area)

        main_layout.addWidget(left_container, 2) 
        main_layout.addWidget(right_container, 1)

        self.refresh_page()

    def refresh_page(self): 
        """Updates UI elements based on current data"""
        self.header.update_money(self.main_window.data['money'])
        
        equipped = self.main_window.data.get('equipped_clothes', [])
        if equipped:
            self.preview_text = "Wearing:\n" + "\n".join(equipped)
            self.preview_area.setText(self.preview_text)
        else:
            self.preview_area.setText("No Clothes Worn")

    def attempt_purchase(self, item_name, item_price):
        if self.main_window.data['money'] >= item_price:
            self.main_window.data['money'] -= item_price
            if item_name not in self.main_window.data['inventory_clothes']:
                self.main_window.data['inventory_clothes'].append(item_name)
            self.refresh_page() 
            self.money_changed.emit(self.main_window.data['money'])
            return True
        else:
            self.preview_area.setText('not suffecient funds')
            return False
        
    def wear_item(self, item_name):
        if item_name not in self.main_window.data['worn_clothes']:
            self.main_window.data['worn_clothes'].append(item_name)
            self.main_window.data['equipped_clothes'].append(item_name)
        self.refresh_page() 
    
    def unwear_item(self, item_name):
        if item_name in self.main_window.data['worn_clothes']:
            self.main_window.data['worn_clothes'].remove(item_name)
            if item_name in self.main_window.data['equipped_clothes']:
                 self.main_window.data['equipped_clothes'].remove(item_name)
        self.refresh_page()