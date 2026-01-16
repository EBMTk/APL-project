from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from store_utils import store_header, HorizontalScrollArea

class FurnitureCard(QFrame):
    def __init__(self, name, price, parent_view, styles):
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles

        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(f"""
                            QFrame {{
                                background-color: {self.styles.col_secondary};
                                border: 1.5px solid {self.styles.col_border};
                                border-radius: 15px;
                            }}
                            QLabel {{ border: none; }}
                            """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        top_layout = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color: {self.styles.col_text}; font-size: 15px; font-weight: bold;")
        price_lbl = QLabel(f"${price}")
        price_lbl.setStyleSheet(f"color: {self.styles.col_text};")
        top_layout.addWidget(name_lbl)
        top_layout.addStretch()
        top_layout.addWidget(price_lbl)

        self.btn_preview = QPushButton("Place")
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preview.setStyleSheet(f"""
            QPushButton {{
                background: {self.styles.col_secondary};
                border: 2px solid {self.styles.col_text};
                border-radius: 8px;
                padding: 5px;
                color: {self.styles.col_text};
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {self.styles.col_hover};}}
        """)
        self.btn_preview.clicked.connect(self.place_item)

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f"""
            QPushButton {{
                background: {self.styles.col_border};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
        self.btn_buy.clicked.connect(self.buy_item)

        layout.addLayout(top_layout)
        layout.addWidget(self.btn_preview)
        layout.addWidget(self.btn_buy)

        self.update_ownership()

    def update_ownership(self):
        count = self.parent_view.main_window.data['inventory_furniture'].count(self.name)
        if count > 0:
            self.btn_buy.setText(f"Buy ({count} Owned)")
        else:
            self.btn_buy.setText("Buy")
    
    def buy_item(self):
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success: self.update_ownership()

    def place_item(self):
        self.parent_view.place_item(self.name)

class FurnitureView(QWidget):
    request_clothing_view = pyqtSignal()
    request_home_view = pyqtSignal()
    money_changed = pyqtSignal(int)

    def __init__(self, main_window, styles):
        super().__init__()
        self.main_window = main_window
        self.styles = styles

        self.furniture_items = {
            "Beds": [("Single Bed", 100), ("Double Bed", 250), ("King Bed", 400)],
            "Chairs": [("Stool", 20), ("Office Chair", 80), ("Gaming Chair", 200)],
            "Tables": [("Side Table", 45), ("Dining Table", 120), ("Glass Table", 150)],
            "Storage": [("Wardrobe", 300), ("Bookshelf", 120), ("Locker", 50)],
            "Decor": [("Rug", 50), ("Painting", 200), ("Vase", 30)],
            "Kitchen": [("Stove", 500), ("Fridge", 600), ("Sink", 300)],
            "Outdoor": [("Bench", 100), ("Fountain", 800), ("Bush", 20)],
            "Office": [("Desk", 150), ("Lamp", 40), ("PC", 1200)],
        }
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.preview = QFrame()
        self.preview.setStyleSheet(self.styles.frame_style())

        preview_layout = QHBoxLayout(self.preview)
        preview_layout.setContentsMargins(20, 20, 20, 20)

        left = QWidget()
        left.setStyleSheet("border: none;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.request_home_view.emit)

        title = QLabel("Furniture Shop")
        title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 20px; font-weight: bold; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.room_label = QLabel("Room Preview Area")
        self.room_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.room_label.setStyleSheet(f"color: {self.styles.col_scroll}; font-size: 24px; font-weight: bold; border: none;")

        self.btn_go_clothing = QPushButton("Browse Clothing")
        self.btn_go_clothing.setFixedHeight(60)
        self.btn_go_clothing.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_clothing.setStyleSheet(self.styles.action_button_style())
        self.btn_go_clothing.clicked.connect(self.request_clothing_view.emit)

        left_layout.addWidget(self.header)
        left_layout.addWidget(title)
        left_layout.addStretch()
        left_layout.addWidget(self.room_label)
        left_layout.addStretch()
        left_layout.addWidget(self.btn_go_clothing)

        self.side_container = QWidget()
        self.side_container.setStyleSheet("border: none;")
        side_layout = QHBoxLayout(self.side_container)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(10)

        self.btn_open_side = QPushButton()
        self.btn_open_side.setFixedSize(7, 70)
        self.btn_open_side.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_side.setStyleSheet(f"background:{self.styles.col_text}; border-radius:3px; border:none;")
        self.btn_open_side.clicked.connect(self.toggle_sidebar)

        self.sidebar_scroll = HorizontalScrollArea()
        self.sidebar_scroll.setFixedWidth(0) 
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sidebar_scroll.setStyleSheet(f"{self.styles.frame_style()} {self.styles.scrollbar_style()}")

        inner = QWidget()
        inner.setStyleSheet("background: transparent; border: none;")
        self.sidebar_layout = QVBoxLayout(inner)
        self.sidebar_layout.setContentsMargins(10, 5, 10, 15)
        self.sidebar_layout.setSpacing(10)

        title_lbl = QLabel("Variants")
        title_lbl.setFixedHeight(25)
        title_lbl.setStyleSheet(f"color: {self.styles.col_text}; font-size: 18px; font-weight: bold; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title_lbl)

        self.sidebar_scroll.setWidget(inner)

        side_layout.addWidget(self.btn_open_side)
        side_layout.addWidget(self.sidebar_scroll)

        preview_layout.addWidget(left,1)
        preview_layout.addWidget(self.side_container)

        self.bottom = QWidget()
        self.bottom.setStyleSheet("border: none;")
        bottom_layout = QVBoxLayout(self.bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setStyleSheet(self.styles.frame_style())
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 10, 0, 10)

        grabber = QPushButton()
        grabber.setFixedSize(80, 6)
        grabber.setCursor(Qt.CursorShape.PointingHandCursor) 
        grabber.setStyleSheet(f"background:{self.styles.col_text}; border-radius:3px; border:none;")
        grabber.clicked.connect(self.toggle_bottom)
        
        self.scroll_container = QWidget()
        self.scroll_container.setMaximumHeight(0) 
        self.scroll_container.setStyleSheet("background: transparent; border: none;")
        scroll_cont_layout = QVBoxLayout(self.scroll_container)
        scroll_cont_layout.setContentsMargins(0,0,0,0)

        self.scroll = HorizontalScrollArea()
        self.scroll.setFixedHeight(145) 
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        cat_widget = QWidget()
        cat_widget.setStyleSheet("background: transparent; border: none;")
        cat_layout = QHBoxLayout(cat_widget)
        cat_layout.setContentsMargins(20, 0, 20, 0)
        cat_layout.setSpacing(15)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for category in self.furniture_items:
            btn = QPushButton(category)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumSize(120, 80)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    background: {self.styles.col_primary}; 
                    border: 2px solid {self.styles.col_border}; 
                    border-radius: 15px; 
                    font-weight: 900; 
                    color: {self.styles.col_text};
                }}
                QPushButton:hover {{ background: {self.styles.col_hover}; }}
            """)
            btn.clicked.connect(lambda _, cat=category: self.load_category(cat))
            cat_layout.addWidget(btn)
        
        self.scroll.setWidget(cat_widget)
        scroll_cont_layout.addWidget(self.scroll)

        frame_layout.addWidget(grabber, 0, Qt.AlignmentFlag.AlignHCenter)
        frame_layout.addWidget(self.scroll_container)

        bottom_layout.addWidget(frame)
        
        main_layout.addWidget(self.preview, 1)
        main_layout.addWidget(self.bottom)

    def toggle_sidebar(self):
        cur = self.sidebar_scroll.width()
        target = 250 if cur == 0 else 0
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.anim1 = QPropertyAnimation(self.sidebar_scroll, b"minimumWidth")
        self.anim2 = QPropertyAnimation(self.sidebar_scroll, b"maximumWidth")
        for a in (self.anim1, self.anim2):
            a.setDuration(450)
            a.setStartValue(cur)
            a.setEndValue(target)
            a.setEasingCurve(QEasingCurve.Type.OutQuint)
            a.finished.connect(lambda: self.on_side_anim_finished(target))
            a.start()
    
    def on_side_anim_finished(self, target):
        if target > 0: self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def toggle_bottom(self):
        cur = self.scroll_container.maximumHeight()
        target = 160 if cur == 0 else 0 
        self.anim_bot = QPropertyAnimation(self.scroll_container, b"maximumHeight")
        self.anim_bot.setDuration(500)
        self.anim_bot.setStartValue(cur)
        self.anim_bot.setEndValue(target)
        self.anim_bot.setEasingCurve(QEasingCurve.Type.OutQuint)
        self.anim_bot.start()

    def load_category(self, category):
        if self.sidebar_scroll.width() == 0: self.toggle_sidebar()
        while self.sidebar_layout.count() > 1:
            item = self.sidebar_layout.takeAt(1).widget()
            if item: item.deleteLater()
        for name, price in self.furniture_items[category]:
            card = FurnitureCard(name, price, self, self.styles)
            self.sidebar_layout.addWidget(card,0,Qt.AlignmentFlag.AlignHCenter)

    def refresh_page(self):
        """Updates UI based on data"""
        self.header.update_money(self.main_window.data['money'])
        placed = self.main_window.data.get('placed_furniture', [])
        if not placed:
            self.room_label.setText("No Furniture Placed")
        else:
            items_text = ", ".join(placed[:])
            count = len(placed)
            self.room_label.setText(f"Placed ({count}): {items_text}")
            self.room_label.setStyleSheet(f"color: {self.styles.col_text}; font-size: 18px; font-weight: bold; border: none;")

    def attempt_purchase(self, item_name, item_price):
        if self.main_window.data['money'] >= item_price:
            self.main_window.data['money'] -= item_price
            self.main_window.data['inventory_furniture'].append(item_name)
            self.refresh_page() 
            self.money_changed.emit(self.main_window.data['money'])
            return True
        else:
            self.room_label.setText('not suffecient funds')
            self.room_label.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none;")
            return False
        
    def place_item(self, item_name):
        owned_qty = self.main_window.data['inventory_furniture'].count(item_name)
        placed_qty = self.main_window.data['placed_furniture'].count(item_name)
        
        if owned_qty == 0:
             self.room_label.setText('Item not owned')
             self.room_label.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none;")
        elif placed_qty < owned_qty:
            self.main_window.data['placed_furniture'].append(item_name)
            self.refresh_page() 
        else:
            self.room_label.setText(f'All {item_name}s placed')
            self.room_label.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none;")