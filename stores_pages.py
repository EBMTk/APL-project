import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QPushButton, QLabel, QHBoxLayout, 
    QLayout, QScrollArea, QVBoxLayout, QApplication, QStackedWidget, 
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal 

### UNIVERSAL_STYLES ###
class UniversalStyles:
    # Combines common styles for reuse and makes applying themes easy
    # Colours
    def __init__(self, primary, secondary, border, hover, text, scroll, scroll_hover):
        self.col_primary = primary
        self.col_secondary = secondary
        self.col_border = border
        self.col_hover = hover
        self.col_text = text
        self.col_scroll = scroll
        self.col_scroll_hover = scroll_hover
        
    # Header Button
    def header_button_style(self):
        return f'''
        QPushButton {{
            background-color: {self.col_primary};
            border: 2px solid {self.col_border};
            font-size: 20px;
            color: {self.col_text};
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        '''
    def money_label_style(self):
        return f'''
        QLabel {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.col_text};
        }}
        '''

    # Frame
    def frame_style(self):
        return f'''
        QFrame {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 25px;
        }}
        '''

    # Button that moves between pages
    def action_button_style(self):
        return f'''
        QPushButton {{
            background-color: {self.col_border};
            color: {self.col_primary};
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        '''

    # Scrollbar
    def scrollbar_style(self):
        return f'''
        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 14px;
            margin: 10px 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {self.col_scroll};
            min-height: 30px;
            border-radius: 7px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {self.col_scroll_hover};
        }}
        /* --- removes side buttons --- */
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
            background: none;
        }}

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: none;
        }}

        /* --- HORIZONTAL SCROLLBAR --- */
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 14px;
            margin: 0px 15px 5px 15px;
        }}

        QScrollBar::handle:horizontal {{
            background: {self.col_scroll};
            min-width: 40px;
            border-radius: 7px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {self.col_scroll_hover};
        }}

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal,
        QScrollBar::left-arrow:horizontal,
        QScrollBar::right-arrow:horizontal {{
            width: 0px;
            height: 0px;
            background: none;
            border: none;
        }}

        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        '''
class store_header(QWidget):
    # Signal when the home button is clicked
    home_clicked = pyqtSignal()

    def __init__(self, styles):
        
        super().__init__()

        self.styles = styles  # store theme object

        # Remove default widget border
        self.setStyleSheet('border: none;')

        # Main horizontal layout for the header
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # no padding around edges
        layout.setSpacing(15)  # space between widgets

        # HOME BUTTON 
        self.btn_home = QPushButton('🏠︎')  # takes button label
        self.btn_home.setFixedSize(50, 50)  # size
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor)  # changes cursor on hover
        self.btn_home.setToolTip('Home')  # hover text
        self.btn_home.setStyleSheet(self.styles.header_button_style())  # theme-based styling
        self.btn_home.clicked.connect(self.home_clicked.emit)  # what happens when clicked

        # MONEY LABEL 
        self.lbl_money = QLabel('$0')  # initial money display when we start saving user data this should be set to that value
        self.lbl_money.setAlignment(Qt.AlignmentFlag.AlignCenter)  # center text
        self.lbl_money.setFixedSize(150, 50)  # width height
        self.lbl_money.setStyleSheet(f'''
            background-color: {self.styles.col_secondary};
            border: 2.5px solid {self.styles.col_text};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.styles.col_text};
        ''')  # we should probably add font styling mb
        # Add them to page
        layout.addWidget(self.btn_home)  # add home button
        layout.addStretch()              # space in the middle
        layout.addWidget(self.lbl_money) # add money label

    # money display update
    def update_money(self, amount):
        '''
        Updates the money with a new amount.
        Args:
            amount: The new money amount to display.
        '''
        self.lbl_money.setText(f'${amount}')

## ALLOW HORIZONTAL SCROLLING##
class HorizontalScrollArea(QScrollArea):
    def wheelEvent(self, event):
      '''turns the movement o the scroll wheel to work on horizontal scrollwheel '''
      delta = event.angleDelta().y()
      if delta != 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()
      else:
            return super().wheelEvent(event)
      
### CLOTHING_CARD ### 
class ClothingCard(QFrame):
    def __init__(self, name, price, parent_view, styles):
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles

        self.setFixedHeight(120)
        # Ensure card fills width of container
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setStyleSheet(f'''
                           QFrame {{
                               background-color: {self.styles.col_secondary};
                               border: 1.5px solid {self.styles.col_border};
                               border-radius: 15px;
                           }}
                           ''')
        layout = QHBoxLayout(self)

        # CLOTHING INFO CARD SETUP
        info_layout = QVBoxLayout()
        self.lbl_name = QLabel(name)
        self.lbl_price = QLabel(f'${price}')
        self.lbl_name.setStyleSheet(f'color: {self.styles.col_text}; font-size: 16px; font-weight: bold; border: none;')
        self.lbl_price.setStyleSheet(f'color: {self.styles.col_text}; font-size: 14px; border: none;')

        info_layout.addWidget(self.lbl_name)
        info_layout.addWidget(self.lbl_price)

        # BUTTON SECTION
        btn_layout = QVBoxLayout()

        # WEAR BUTTON
        self.btn_wear = QPushButton('Wear')
        self.btn_wear.setCursor(Qt.CursorShape.PointingHandCursor)
        # Default Style
        self.btn_wear.setStyleSheet(f'''
        QPushButton {{
            background: {self.styles.col_secondary};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_text};
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        QPushButton:disabled {{
            background: #cccccc;
            color: #888888;
        }}
        ''')
        self.btn_wear.clicked.connect(self.try_item)

        # BUY BUTTON
        self.btn_buy = QPushButton('Buy')
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f'''
        QPushButton {{
            background: {self.styles.col_border};
            color: {self.styles.col_primary};
            border:none;
            border-radius: 8px;
            font-weight: bold;
            padding: 4px;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        QPushButton:disabled {{
            background: #cccccc;
            color: #888888;
        }}
        ''')
        self.btn_buy.clicked.connect(self.buy_item)
        
        btn_layout.addWidget(self.btn_wear)
        btn_layout.addWidget(self.btn_buy)

        layout.addLayout(info_layout)
        layout.addLayout(btn_layout) 

        #Check ownership and if its OWNED disable buy button
        if self.name in self.parent_view.main_window.data['inventory_clothes']:
            self.set_owned_state()
        
        #Check if it is on 
        if self.name in self.parent_view.main_window.data['worn_clothes']:
            self.set_worn_state()

    def set_owned_state(self):
        '''UI changes when item is owned'''
        self.btn_buy.setText('Owned')
        self.btn_buy.setDisabled(True)
        self.lbl_price.setText('In Inventory')
        
    def set_worn_state(self):
        '''UI changes when item is being worn'''
        self.btn_wear.setText('Take Off')
        # Dark style for 'Take Off' state
        self.btn_wear.setStyleSheet(f'''
        QPushButton {{
            background: {self.styles.col_text};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_secondary};
            font-weight: bold;
        }}
        QPushButton:hover {{ opacity: 0.9; }}
        ''')

    def set_unworn_state(self):
        '''UI changes when an owned item is NOT being worn'''
        self.btn_wear.setText('Wear')
        # Revert to default light style
        self.btn_wear.setStyleSheet(f'''
        QPushButton {{
            background: {self.styles.col_secondary};
            border: 2px solid {self.styles.col_text};
            border-radius: 8px;
            padding: 4px;
            color: {self.styles.col_text};
            font-weight: bold;
        }}
        QPushButton:hover {{ background: {self.styles.col_hover};}}
        ''')
    
    def buy_item(self):
        '''Buys item'''
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success:
            self.set_owned_state()
    
    def try_item(self):
        '''Puts on and off clothes'''
        if self.btn_wear.text() == 'Take Off':
            self.parent_view.unwear_item(self.name)
            self.set_unworn_state()
        else:
            self.parent_view.wear_item(self.name)
            self.set_worn_state()
    
### FURNITURE CARD ###
class FurnitureCard(QFrame):
    '''Card for each furniture item in the shop'''
    def __init__(self, name, price, parent_view, styles):
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles

        self.setFixedHeight(130)
        # REMOVED FIXED WIDTH -> Now it will stretch to fill sidebar
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(f'''
                           QFrame {{
                               background-color: {self.styles.col_secondary};
                               border: 1.5px solid {self.styles.col_border};
                               border-radius: 15px;
                           }}
                           QLabel {{ border: none; }}
                           ''')
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # CARD HEADER
        top_layout = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f'color: {self.styles.col_text}; font-size: 15px; font-weight: bold;')
        price_lbl = QLabel(f'${price}')
        price_lbl.setStyleSheet(f'color: {self.styles.col_text};')
        top_layout.addWidget(name_lbl)
        top_layout.addStretch()
        top_layout.addWidget(price_lbl)

        # PLACE BUTTONS
        self.btn_preview = QPushButton('Place')
        self.btn_preview.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_preview.setStyleSheet(f'''
            QPushButton {{
                background: {self.styles.col_secondary};
                border: 2px solid {self.styles.col_text};
                border-radius: 8px;
                padding: 5px;
                color: {self.styles.col_text};
                font-weight: bold;
            }}
            QPushButton:hover {{ background: {self.styles.col_hover};}}
        ''')
        self.btn_preview.clicked.connect(self.place_item)

        # BUY BUTTON
        self.btn_buy = QPushButton('Buy')
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(f'''
            QPushButton {{
                background: {self.styles.col_border};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{ opacity: 0.8; }}
        ''')
        self.btn_buy.clicked.connect(self.buy_item)

        layout.addLayout(top_layout)
        layout.addWidget(self.btn_preview)
        layout.addWidget(self.btn_buy)

        # CHECK OWNERSHIP
        self.update_ownership()

    def update_ownership(self):
        ''' Update button to show owned count'''
        count = self.parent_view.main_window.data['inventory_furniture'].count(self.name)
        if count > 0:
            self.btn_buy.setText(f'Buy ({count} Owned)')
            self.btn_buy.setDisabled(False) 
        else:
            self.btn_buy.setText('Buy')
            self.btn_buy.setDisabled(False)
    
    def buy_item(self):
        '''Attempts to buy the furniture item'''
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success:
            self.update_ownership()

    def place_item(self):
        '''Previews the furniture item in the room'''
        self.parent_view.place_item(self.name)

### CLOTHING_VIEW ###
class ClothingView(QWidget):
    request_furniture_view = pyqtSignal()
    request_home_view = pyqtSignal()
    money_changed = pyqtSignal(int)

    def __init__(self, main_window, styles):
        super().__init__()
        self.main_window = main_window
        self.styles = styles

        #Clothing items data
        self.clothing_items = [
            ('T-Shirt', 20),
            ('Jeans', 40),
            ('Jacket', 60),
            ('Sneakers', 50),
            ('Hat', 15),
            ('Sunglasses', 25),
            ('Dress', 70),
            ('Boots', 80),
        ]
        self.init_ui()

    def init_ui(self):
        # MAIN LAYOUT (Changed to Horizontal to match reference)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LEFT SECTION (Preview, Header, Nav)
        left_container = QFrame()
        left_container.setStyleSheet(self.styles.frame_style())
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(20, 20, 20, 20)

        # HEADER
        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.request_home_view.emit)

        #TITLE 
        title = QLabel('Clothing Shop')
        title.setStyleSheet(f'color: {self.styles.col_text}; font-size: 20px; font-weight: bold;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # PREVIEW AREA
        self.preview_area = QLabel('Try Item')
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setStyleSheet(f'''background: transparent;
                                           border: none;
                                           color: {self.styles.col_text};
                                           font-size: 18px;
                                           ''')
        self.refresh_preview()

        #NAVIGATION BUTTONS
        self.btn_go_furniture = QPushButton('Browse Furniture')
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

        # RIGHT SECTION (clothing items list)
        right_container = QFrame()
        # REMOVED FIXED WIDTH to allow resizing
        # right_container.setFixedWidth(350) 
        right_container.setStyleSheet(self.styles.frame_style())
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 20, 20, 20)

        # TITTLE
        right_title = QLabel('Available Clothing')
        right_title.setStyleSheet(f'color: {self.styles.col_text}; font-size: 22px; font-weight: bold; border: none;')
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # SCROLL AREA FOR CLOTHING ITEMS
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(self.styles.scrollbar_style())

        # ITEM CONTAINER
        item_container = QWidget()
        item_container.setStyleSheet('background: transparent; ')
        item_layout = QVBoxLayout(item_container)
        item_layout.setSpacing(10)

        # ADD CLOTHING CARDS
        for name, price in self.clothing_items:
            card = ClothingCard(name, price, self, self.styles)
            item_layout.addWidget(card)

        item_layout.addStretch()  # push items to top
        scroll_area.setWidget(item_container)

        right_layout.addWidget(right_title)
        right_layout.addWidget(scroll_area)

        # Add containers to main horizontal layout WITH STRETCH FACTORS
        main_layout.addWidget(left_container, 2)  # Takes 2/3 space
        main_layout.addWidget(right_container, 1) # Takes 1/3 space, but is flexible

    def update_money(self):
        '''Updates the money display in the header'''
        self.header.update_money(self.main_window.data['money'])
        self.refresh_preview()

    def refresh_preview(self):
        '''Updated the preview area with currently worn clothes'''
        equipped = self.main_window.data.get('equipped_clothes', [])
        if equipped:
            self.preview_text = 'Wearing:\n' + '\n'.join(equipped)
            self.preview_area.setText(self.preview_text)
        else:
            self.preview_area.setText('No Clothes Worn')
    
    def attempt_purchase(self, item_name, item_price):
        '''Attempts to purchase an item'''
        if self.main_window.data['money'] >= item_price:
            self.main_window.data['money'] -= item_price
            if item_name not in self.main_window.data['inventory_clothes']:
                self.main_window.data['inventory_clothes'].append(item_name)

            self.update_money()
            self.money_changed.emit(self.main_window.data['money'])
            return True
        else:
            self.preview_area.setText('not suffecient funds')
            return False
        
    def wear_item(self, item_name):
        '''Wears a clothing item'''
        if item_name not in self.main_window.data['worn_clothes']:
            self.main_window.data['worn_clothes'].append(item_name)
            self.main_window.data['equipped_clothes'].append(item_name)
        self.refresh_preview()
    
    def unwear_item(self, item_name):
        '''Removes a clothing item'''
        if item_name in self.main_window.data['worn_clothes']:
            self.main_window.data['worn_clothes'].remove(item_name)
            if item_name in self.main_window.data['equipped_clothes']:
                 self.main_window.data['equipped_clothes'].remove(item_name)
        self.refresh_preview()

### FURNITURE_VIEW ###
class FurnitureView(QWidget):
    # Navigation signals
    request_clothing_view = pyqtSignal()
    request_home_view = pyqtSignal()
    money_changed = pyqtSignal(int)

    def __init__(self, main_window, styles):
        super().__init__()
        self.main_window = main_window
        self.styles = styles

        #Furniture items data
        self.furniture_items = {
            'Beds': [('Single Bed', 100), ('Double Bed', 250), ('King Bed', 400)],
            'Chairs': [('Stool', 20), ('Office Chair', 80), ('Gaming Chair', 200)],
            'Tables': [('Side Table', 45), ('Dining Table', 120), ('Glass Table', 150)],
            'Storage': [('Wardrobe', 300), ('Bookshelf', 120), ('Locker', 50)],
            'Decor': [('Rug', 50), ('Painting', 200), ('Vase', 30)],
            'Kitchen': [('Stove', 500), ('Fridge', 600), ('Sink', 300)],
            'Outdoor': [('Bench', 100), ('Fountain', 800), ('Bush', 20)],
            'Office': [('Desk', 150), ('Lamp', 40), ('PC', 1200)],
        }

        self.init_ui()

    def init_ui(self):
        # MAIN LAYOUT
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # PREVIEW AREA
        self.preview = QFrame()
        self.preview.setStyleSheet(self.styles.frame_style())

        preview_layout = QHBoxLayout(self.preview)
        preview_layout.setContentsMargins(20, 20, 20, 20)


        # LEFT SIDE (Header + Title + Navigation)
        left = QWidget()
        left.setStyleSheet('border: none;')
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # HEADER (home button + money display)
        self.header = store_header(self.styles)
        self.header.home_clicked.connect(self.request_home_view.emit)

        #TITLE
        title = QLabel('Furniture Shop')
        title.setStyleSheet(f'color: {self.styles.col_text}; font-size: 20px; font-weight: bold; border: none;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ROOM LABEL (shows items)
        self.room_label = QLabel('Room Preview Area')
        self.room_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.room_label.setStyleSheet(f'color: {self.styles.col_scroll}; font-size: 24px; font-weight: bold; border: none;')

        #NAVIGATION BUTTONS
        self.btn_go_clothing = QPushButton('Browse Clothing')
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

        # SIDE SECTION (furniture items list)
        self.side_container = QWidget()
        self.side_container.setStyleSheet('border: none;')
        side_layout = QHBoxLayout(self.side_container)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(10)

        # SIDE OPEN BUTTON
        self.btn_open_side = QPushButton()
        self.btn_open_side.setFixedSize(7, 70)
        self.btn_open_side.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_side.setStyleSheet(f'background:{self.styles.col_text}; border-radius:3px; border:none;')
        self.btn_open_side.clicked.connect(self.toggle_sidebar)

        # SIDEBARD SCROLL AREA
        self.sidebar_scroll = QScrollArea()
        self.sidebar_scroll.setFixedWidth(0)  # starts closed
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.sidebar_scroll.setStyleSheet((f'''
            {self.styles.frame_style()}
            {self.styles.scrollbar_style()}
        '''))

        # SIDEBAR INNER CONTAINER
        inner = QWidget()
        inner.setStyleSheet('background: transparent; border: none;')
        self.sidebar_layout = QVBoxLayout(inner)
        self.sidebar_layout.setContentsMargins(10, 5, 10, 15)
        self.sidebar_layout.setSpacing(10)

        # SIDEBAR TTILE
        title_lbl = QLabel('Variants')
        title_lbl.setFixedHeight(25)
        title_lbl.setStyleSheet(f'color: {self.styles.col_text}; font-size: 18px; font-weight: bold; border: none;')
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title_lbl)

        self.sidebar_scroll.setWidget(inner)

        side_layout.addWidget(self.btn_open_side)
        side_layout.addWidget(self.sidebar_scroll)

        preview_layout.addWidget(left,1)
        preview_layout.addWidget(self.side_container)

        # BOTTOM DRAWER (category selection)
        self.bottom = QWidget()
        self.bottom.setStyleSheet('border: none;')
        bottom_layout = QVBoxLayout(self.bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # DRAWER FRAME
        frame = QFrame()
        frame.setStyleSheet(self.styles.frame_style())
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 10, 0, 10)

        # DRAWER GRABBER (button to open/close)
        grabber = QPushButton()
        grabber.setFixedSize(80, 6)
        grabber.setCursor(Qt.CursorShape.PointingHandCursor) 
        grabber.setStyleSheet(f'background:{self.styles.col_text}; border-radius:3px; border:none;')
        grabber.clicked.connect(self.toggle_bottom)
        
        # SCROLL CONTAINER (starts closed)
        self.scroll_container = QWidget()
        self.scroll_container.setMaximumHeight(0) 
        self.scroll_container.setStyleSheet('background: transparent; border: none;')
        scroll_cont_layout = QVBoxLayout(self.scroll_container)
        scroll_cont_layout.setContentsMargins(0,0,0,0)

        # HORIZONTAL SCROLL AREA (for categories)
        self.scroll = HorizontalScrollArea()
        self.scroll.setFixedHeight(145) 
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.scroll.setStyleSheet('background: transparent; border: none;')

        # CATEGORIED CONTAINER
        cat_widget = QWidget()
        cat_widget.setStyleSheet('background: transparent; border: none;')
        cat_layout = QHBoxLayout(cat_widget)
        cat_layout.setContentsMargins(20, 0, 20, 0)
        cat_layout.setSpacing(15)
        cat_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ADD CATEGORY BUTTONS
        for category in self.furniture_items:
            btn = QPushButton(category)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # CHANGED: From FixedSize to MinimumSize + Expanding Policy
            btn.setMinimumSize(120, 80)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            btn.setStyleSheet(f'''
                QPushButton {{ 
                    background: {self.styles.col_primary}; 
                    border: 2px solid {self.styles.col_border}; 
                    border-radius: 15px; 
                    font-weight: 900; 
                    color: {self.styles.col_text};
                }}
                QPushButton:hover {{ background: {self.styles.col_hover}; }}
            ''')
            btn.clicked.connect(lambda _, cat=category: self.load_category(cat))
            cat_layout.addWidget(btn)
        
        self.scroll.setWidget(cat_widget)
        scroll_cont_layout.addWidget(self.scroll)

        frame_layout.addWidget(grabber, 0, Qt.AlignmentFlag.AlignHCenter)
        frame_layout.addWidget(self.scroll_container)

        bottom_layout.addWidget(frame)
        
        main_layout.addWidget(self.preview, 1)
        main_layout.addWidget(self.bottom)

    ########ANIMATIONS NOT SURE HOW THEY WORK NGLL########    

    # ANIMATION: Toggle sidebar open/closed
    def toggle_sidebar(self):
        cur = self.sidebar_scroll.width()
        target = 250 if cur == 0 else 0
        self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.anim1 = QPropertyAnimation(self.sidebar_scroll, b'minimumWidth')
        self.anim2 = QPropertyAnimation(self.sidebar_scroll, b'maximumWidth')
        for a in (self.anim1, self.anim2):
            a.setDuration(450)
            a.setStartValue(cur)
            a.setEndValue(target)
            a.setEasingCurve(QEasingCurve.Type.OutQuint)
            a.finished.connect(lambda: self.on_side_anim_finished(target))
            a.start()
    
    def on_side_anim_finished(self, target):
        '''Enables scrollbar if sidebar is open'''
        if target > 0:
            self.sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)


    # ANIMATION: Toggle bottom drawer open/closed
    def toggle_bottom(self):
        cur = self.scroll_container.maximumHeight()
        target = 160 if cur == 0 else 0 
        
        self.anim_bot = QPropertyAnimation(self.scroll_container, b'maximumHeight')
        self.anim_bot.setDuration(500)
        self.anim_bot.setStartValue(cur)
        self.anim_bot.setEndValue(target)
        self.anim_bot.setEasingCurve(QEasingCurve.Type.OutQuint)
        self.anim_bot.start()

    def load_category(self, category):
        '''Loads furniture items of a specific category into the sidebar'''
        # open sidebar if closed
        if self.sidebar_scroll.width() == 0:
            self.toggle_sidebar()

        # Clear existing items
        while self.sidebar_layout.count() > 1:
            item = self.sidebar_layout.takeAt(1).widget()
            if item: item.deleteLater()

        # Add new furniture items
        for name, price in self.furniture_items[category]:
            card = FurnitureCard(name, price, self, self.styles)
            self.sidebar_layout.addWidget(card,0,Qt.AlignmentFlag.AlignHCenter)

    def update_money(self):
        '''Updates the money display in the header'''
        self.header.update_money(self.main_window.data['money'])
        self.refresh_room_preview() 

    def refresh_room_preview(self):
        '''Updates the room preview area with currently placed furniture'''
        placed = self.main_window.data.get('placed_furniture', [])
        if not placed:
            self.room_label.setText('No Furniture Placed')
        else:
            items_text = ', '.join(placed[:])
            count = len(placed)
            self.room_label.setText(f'Placed ({count}): {items_text}')
            self.room_label.setStyleSheet(f'color: {self.styles.col_text}; font-size: 18px; font-weight: bold; border: none;')

    
    # BUYING STUFF
    def attempt_purchase(self, item_name, item_price):
        '''Attempts to purchase an item'''
        if self.main_window.data['money'] >= item_price:
            self.main_window.data['money'] -= item_price
            self.main_window.data['inventory_furniture'].append(item_name)

            self.update_money()
            self.money_changed.emit(self.main_window.data['money'])
            return True
        else:
            self.room_label.setText('not suffecient funds')
            self.room_label.setStyleSheet(f'color: red; font-size: 24px; font-weight: bold; border: none;')
            return False
        
    # PLACE FURNITURE
    def place_item(self, item_name):
        '''Places a furniture item in the room'''
        owned_qty = self.main_window.data['inventory_furniture'].count(item_name)
        placed_qty = self.main_window.data['placed_furniture'].count(item_name)
        
        if owned_qty == 0:
             self.room_label.setText('Item not owned')
             self.room_label.setStyleSheet(f'color: red; font-size: 24px; font-weight: bold; border: none;')
        elif placed_qty < owned_qty:
            self.main_window.data['placed_furniture'].append(item_name)
            self.refresh_room_preview()
        else:
            self.room_label.setText(f'All {item_name}s placed')
            self.room_label.setStyleSheet(f'color: red; font-size: 24px; font-weight: bold; border: none;')

### MAIN WINDOW###
class MainShopsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TikiT Stores')
        self.resize(1100, 750)

        #Initialize Theme
        self.styles = UniversalStyles(
            primary='#f8f8f8',
            secondary='#ffffff',
            border='#000000',
            hover='#f0f0f0',
            text='#000000',
            scroll='#888888',
            scroll_hover='#555555'
        )

        self.setStyleSheet(f'background-color: {self.styles.col_primary};')

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
        '''Switches between furniture and clothing views'''
        if index == 0:
            self.view_furniture.update_money()
        elif index == 1:
            self.view_furniture.update_money()

        self.stack.setCurrentIndex(index)

    def sync_money(self):
        '''Makes money same throughout views'''
        self.view_clothing.update_money()
        self.view_furniture.update_money()


### FINALLYYY MAIN EXECUTION ###
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainShopsWindow()
    w.show()
    sys.exit(app.exec())
