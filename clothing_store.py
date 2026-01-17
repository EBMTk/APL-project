from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap 
from store_utils import store_header, default_theme

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
        self.btn_action = QPushButton("Try") 
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.clicked.connect(self.handle_action)

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f"QPushButton {{ background: {self.styles.col_border}; color: {self.styles.col_primary}; border:none; border-radius: 8px; font-weight: bold; padding: 4px; }} QPushButton:hover {{ background: {self.styles.col_hover};}}")
        self.btn_buy.clicked.connect(self.buy_item)
        
        btn_layout.addWidget(self.btn_action)
        btn_layout.addWidget(self.btn_buy)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout) 
        self.update_card_state()

    def update_card_state(self):
        data = self.parent_view.clothes_data
        is_owned = self.name in data.inventory_clothes
        is_active = self.name in data.worn_clothes

        if is_owned:
            self.btn_buy.setText("Owned")
            self.btn_buy.setDisabled(True)
            self.lbl_price.setText("In Inventory")
        else:
            self.btn_buy.setText("Buy")
            self.btn_buy.setEnabled(True)
            self.lbl_price.setText(f"${self.price}")

        if is_active:
            self.btn_action.setText("Take Off")
            self.btn_action.setStyleSheet(f"QPushButton {{ background: {self.styles.col_text}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_secondary}; font-weight: bold; }}")
        else:
            self.btn_action.setText("Wear" if is_owned else "Try")
            self.btn_action.setStyleSheet(f"QPushButton {{ background: {self.styles.col_secondary}; border: 2px solid {self.styles.col_text}; border-radius: 8px; padding: 4px; color: {self.styles.col_text}; font-weight: bold; }}")

    def buy_item(self):
        if self.parent_view.attempt_purchase(self.name, self.price):
            self.update_card_state()
    
    def handle_action(self):
        if self.btn_action.text() == "Take Off":
            self.parent_view.unwear_item(self.name)
        else:
            self.parent_view.wear_item(self.name)

class ClothingView(QWidget):
    request_furniture_view = pyqtSignal()
    request_home_view = pyqtSignal()
    checkout_completed = pyqtSignal(dict, dict)
    money_changed = pyqtSignal(int)

    #omarrrrrrrrrrr
    def __init__(self, clothes_data, styles=default_theme): 
        super().__init__()
        self.clothes_data = clothes_data #omar
        self.styles = styles
        
        # Save snapshot of what was worn upon load
        self.original_outfit = dict(self.clothes_data.equipped_clothes) if hasattr(self.clothes_data, 'equipped_clothes') else {}

        self.category_map = {
            "Head": ["Hat", "Sunglasses", "Kanye", "Silly", "Crazy"],
            "Torso": ["T-Shirt", "sweater"],
            "Legs": ["Jeans", "skirt"],
            "Feet": ["Sneakers", "Boots"]
        }

        self.clothing_items = [
            ("T-Shirt", 20), ("Jeans", 40), ("sweater", 60), ("Sneakers", 50),
            ("Hat", 15), ("Sunglasses", 25), ("skirt", 70), ("Boots", 80),
            ("Kanye", 300), ("Silly", 5), ("Crazy", 70)
        ]
        
        self.cards = {} 
        self.init_ui()

    def update_clothes_data(self, game_data):
        self.clothes_data = game_data
        self.original_outfit = dict(self.clothes_data.equipped_clothes) if hasattr(self.clothes_data, 'equipped_clothes') else {}

    def finalize_checkout(self):
        #OMARRRRRR 
        inv = self.clothes_data.inventory_clothes
        inventory_dict = inv if isinstance(inv, dict) else {item: True for item in inv}

        current_worn = self.clothes_data.worn_clothes
        final_equipped = {}

        for category, items in self.category_map.items():
            active = next((i for i in current_worn if i in items), None)
            if active and active in inventory_dict:
                final_equipped[category] = active
            else:
                final_equipped[category] = self.original_outfit.get(category)
        
        self.clothes_data.equipped_clothes = final_equipped
        self.clothes_data.worn_clothes = [v for v in final_equipped.values() if v]

        print(f"\nInventory Sent: {inventory_dict}")
        print(f"Equipped Sent: {final_equipped}\n")

        # Emit the signal to Main
        self.checkout_completed.emit(inventory_dict, final_equipped)

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_container = QFrame()
        left_container.setStyleSheet(self.styles.frame_style())
        left_layout = QVBoxLayout(left_container)

        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.handle_home_click)
        left_layout.addWidget(self.header)

        self.preview_container = QWidget()
        self.preview_vbox = QVBoxLayout(self.preview_container)
        self.preview_vbox.setSpacing(0)
        self.preview_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slots = {}
        dims = {"Head": (200, 154), "Torso": (200, 139), "Legs": (200, 139), "Feet": (200, 45)}
        for part, (w, h) in dims.items():
            lbl = QLabel()
            lbl.setFixedSize(w, h)
            lbl.setScaledContents(True)
            lbl.setStyleSheet("border: none; background: transparent;")
            self.slots[part] = lbl
            self.preview_vbox.addWidget(lbl)

        left_layout.addStretch()
        left_layout.addWidget(self.preview_container)
        left_layout.addStretch()

        self.btn_go_furniture = QPushButton("Browse Furniture")
        self.btn_go_furniture.setStyleSheet(self.styles.action_button_style())
        self.btn_go_furniture.setFixedHeight(60)
        self.btn_go_furniture.clicked.connect(self.handle_furniture_click)
        left_layout.addWidget(self.btn_go_furniture)

        right_container = QFrame()
        right_container.setStyleSheet(self.styles.frame_style())
        right_layout = QVBoxLayout(right_container)

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

    def handle_home_click(self):
        self.finalize_checkout()
        self.request_home_view.emit()

    def handle_furniture_click(self):
        self.finalize_checkout()
        self.request_furniture_view.emit()

    def wear_item(self, item_name):
        cat = self.get_category_of(item_name)
        self.clothes_data.worn_clothes = [i for i in self.clothes_data.worn_clothes if self.get_category_of(i) != cat]
        self.clothes_data.worn_clothes.append(item_name)
        self.refresh_page()

    def unwear_item(self, item_name):
        if item_name in self.clothes_data.worn_clothes:
            self.clothes_data.worn_clothes.remove(item_name)
        self.refresh_page()

    def attempt_purchase(self, item_name, item_price):
        if self.clothes_data.money >= item_price:
            self.clothes_data.money -= item_price
            if isinstance(self.clothes_data.inventory_clothes, dict):
                self.clothes_data.inventory_clothes[item_name] = True
            else:
                self.clothes_data.inventory_clothes.append(item_name)
            self.money_changed.emit(self.clothes_data.money)
            self.refresh_page()
            return True
        return False

    def get_category_of(self, item_name):
        for category, items in self.category_map.items():
            if item_name in items: return category
        return None

    def refresh_page(self): 
        self.header.update_money(self.clothes_data.money)
        for part, label in self.slots.items():
            active_item = next((i for i in self.clothes_data.worn_clothes if self.get_category_of(i) == part), None)
            img_name = active_item.lower() if active_item else f"base_{part.lower()}"
            pixmap = QPixmap(f"assets/{img_name}.png")
            if not pixmap.isNull():
                label.setPixmap(pixmap)
            else:
                label.clear()
        for card in self.cards.values():
            card.update_card_state()