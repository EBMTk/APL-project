from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap 
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

        self.setStyleSheet(f"QFrame {{ background-color: {self.styles.col_secondary}; border: 1.5px solid {self.styles.col_border}; border-radius: 15px; }}")
        
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
        self.btn_wear.setStyleSheet(self.get_unworn_style())
        self.btn_wear.clicked.connect(self.try_item)

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f"QPushButton {{ background: {self.styles.col_border}; color: {self.styles.col_primary}; border:none; border-radius: 8px; font-weight: bold; padding: 4px; }} QPushButton:hover {{ background: {self.styles.col_hover};}}")
        self.btn_buy.clicked.connect(self.buy_item)
        
        btn_layout.addWidget(self.btn_wear)
        btn_layout.addWidget(self.btn_buy)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout) 

        # Initial State Check
        if self.name in self.parent_view.main_window.data['inventory_clothes']:
            self.set_owned_state()
        if self.name in self.parent_view.main_window.data['worn_clothes']:
            self.set_worn_state()

    def get_unworn_style(self):
        return f"QPushButton {{ background: {self.styles.col_secondary}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_text}; font-weight: bold; }} QPushButton:hover {{ background: {self.styles.col_hover};}}"

    def set_owned_state(self):
        self.btn_buy.setText("Owned")
        self.btn_buy.setDisabled(True)
        self.lbl_price.setText("In Inventory")
        
    def set_worn_state(self):
        self.btn_wear.setText("Take Off")
        self.btn_wear.setStyleSheet(f"QPushButton {{ background: {self.styles.col_text}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_secondary}; font-weight: bold; }}")

    def set_unworn_state(self):
        self.btn_wear.setText("Wear")
        self.btn_wear.setStyleSheet(self.get_unworn_style())
    
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

        # 1. Define Categories for the Graphical Slots
        self.category_map = {
            "Head": ["Hat", "Sunglasses"],
            "Torso": ["T-Shirt", "sweater"],
            "Legs": ["Jeans", "skirt"],
            "Feet": ["Sneakers", "Boots"]
        }

        # 2. Items list with original names
        self.clothing_items = [
            ("T-Shirt", 20), ("Jeans", 40), ("sweater", 60), ("Sneakers", 50),
            ("Hat", 15), ("Sunglasses", 25), ("skirt", 70), ("Boots", 80),
        ]
        
        self.cards = {} 
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- LEFT SIDE (Graphical Preview) ---
        left_container = QFrame()
        left_container.setStyleSheet(self.styles.frame_style())
        left_layout = QVBoxLayout(left_container)

        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.request_home_view.emit)
        left_layout.addWidget(self.header)

        # Graphical Slots Container
        self.preview_container = QWidget()
        self.preview_vbox = QVBoxLayout(self.preview_container)
        self.preview_vbox.setSpacing(0)
        self.preview_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slots = {}
        for part in ["Head", "Torso", "Legs", "Feet"]:
            lbl = QLabel()
            lbl.setFixedSize(250, 130) # Increase size if your PNGs are large
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.slots[part] = lbl
            self.preview_vbox.addWidget(lbl)

        left_layout.addStretch()
        left_layout.addWidget(self.preview_container)
        left_layout.addStretch()

        self.btn_go_furniture = QPushButton("Browse Furniture")
        self.btn_go_furniture.setStyleSheet(self.styles.action_button_style())
        self.btn_go_furniture.clicked.connect(self.request_furniture_view.emit)
        self.btn_go_furniture.setFixedHeight(60)
        left_layout.addWidget(self.btn_go_furniture)

        # --- RIGHT SIDE (The Shop List) ---
        right_container = QFrame()
        right_container.setStyleSheet(self.styles.frame_style())
        right_layout = QVBoxLayout(right_container)

        right_title = QLabel("Available Clothing")
        right_title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 22px; font-weight: bold; border: none;")
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(right_title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.styles.scrollbar_style())

        item_container = QWidget()
        item_layout = QVBoxLayout(item_container)
        
        for name, price in self.clothing_items:
            card = ClothingCard(name, price, self, self.styles)
            item_layout.addWidget(card)
            self.cards[name] = card 

        item_layout.addStretch()
        scroll_area.setWidget(item_container)
        right_layout.addWidget(scroll_area)

        main_layout.addWidget(left_container, 2)
        main_layout.addWidget(right_container, 1)

        self.refresh_page()

    def get_category_of(self, item_name):
        for category, items in self.category_map.items():
            if item_name in items: return category
        return None

    def wear_item(self, item_name):
        category = self.get_category_of(item_name)
        worn_list = self.main_window.data['worn_clothes']
        equipped_list = self.main_window.data['equipped_clothes']

        # Remove item from the SAME category (Mutual Exclusion)
        for already_worn in list(worn_list):
            if self.get_category_of(already_worn) == category:
                worn_list.remove(already_worn)
                if already_worn in equipped_list:
                    equipped_list.remove(already_worn)
                if already_worn in self.cards:
                    self.cards[already_worn].set_unworn_state()

        worn_list.append(item_name)
        equipped_list.append(item_name)
        self.refresh_page()

    def unwear_item(self, item_name):
        if item_name in self.main_window.data['worn_clothes']:
            self.main_window.data['worn_clothes'].remove(item_name)
            if item_name in self.main_window.data['equipped_clothes']:
                 self.main_window.data['equipped_clothes'].remove(item_name)
        self.refresh_page()

    def refresh_page(self): 
        self.header.update_money(self.main_window.data['money'])
        worn = self.main_window.data.get('worn_clothes', [])

        for part, label in self.slots.items():
            active_item = next((item for item in worn if self.get_category_of(item) == part), None)
            
            # Use lower-case name for file searching
            img_name = active_item.lower() if active_item else f"base_{part.lower()}"
            img_path = f"assets/{img_name}.png"
            
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                label.setText(f"Missing: {img_name}.png") # Debug text if file not found

    def attempt_purchase(self, item_name, item_price):
        if self.main_window.data['money'] >= item_price:
            self.main_window.data['money'] -= item_price
            if item_name not in self.main_window.data['inventory_clothes']:
                self.main_window.data['inventory_clothes'].append(item_name)
            self.refresh_page() 
            self.money_changed.emit(self.main_window.data['money'])
            return True
        return False