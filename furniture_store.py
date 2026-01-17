from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, 
    QVBoxLayout, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
from store_utils import store_header, HorizontalScrollArea, default_theme
import os
from PyQt6.QtGui import QPixmap

class FurnitureCard(QFrame):
    def __init__(self, name, price, image_paths, parent_view, styles):
        super().__init__()
        self.name = name
        self.price = price
        self.parent_view = parent_view
        self.styles = styles
        self.image_paths = image_paths

        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.setStyleSheet(f"""
                            QFrame {{
                                background-color: {self.styles.col_secondary};
                                border: 1.5px solid {self.styles.col_border};
                                border-radius: 15px;
                            }}
                            QLabel {{ border: none; background: transparent; }}
                            """) #should prob be moved to styles later
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        #added image preview
        self.img_lbl = QLabel()
        self.img_lbl.setFixedSize(100, 100)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if image_paths:
            pixmap = QPixmap(image_paths[0])
            scaled_pixmap = pixmap.scaled(90,90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.img_lbl.setPixmap(scaled_pixmap)
    
        
        layout.addWidget(self.img_lbl)

        right_layout = QWidget()
        right_layout.setStyleSheet("border: none; background: transparent;")
        right_layout_v = QVBoxLayout(right_layout)
        right_layout_v.setContentsMargins(0, 0, 0, 0)

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
        self.btn_preview.clicked.connect(lambda: self.parent_view.place_item(self.name, self.image_paths))

        self.btn_buy = QPushButton("Buy")
        self.btn_buy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buy.setStyleSheet(self.styles.button_style())
        self.btn_buy.clicked.connect(self.buy_item)

        right_layout_v.addLayout(top_layout)
        right_layout_v.addWidget(self.btn_preview)
        right_layout_v.addWidget(self.btn_buy)

        layout.addWidget(right_layout,1)
        self.update_ownership()

    def update_ownership(self):
        count = self.parent_view.game_data.inventory_furniture.count(self.name)
        if count > 0:
            self.btn_buy.setText(f"Buy ({count} Owned)")
        else:
            self.btn_buy.setText("Buy")
    
    def buy_item(self):
        success = self.parent_view.attempt_purchase(self.name, self.price)
        if success: self.update_ownership()

class FurnitureView(QWidget):
    request_clothing_view = pyqtSignal()
    request_home_view = pyqtSignal()
    request_save_layout = pyqtSignal(list, list)
    money_changed = pyqtSignal(int)

    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.styles = default_theme

        self.furniture_items = self.load_item_image()
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

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

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Furniture Shop")
        title.setStyleSheet(f"color: {self.styles.col_text}; font-size: 20px; font-weight: bold; border: none;")
        
        self.btn_save = QPushButton('Save Changes')
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_save.setStyleSheet(self.styles.button_style())
        self.btn_save.clicked.connect(self.save_layout)

        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        title_row_layout.addWidget(self.btn_save)  

        self.room_area = QFrame()
        self.room_area.setStyleSheet(f'background-color: {self.styles.col_primary}; border: 2px solid {self.styles.col_border}; border-radius:10px;')
        self.room_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.room_layout = QVBoxLayout(self.room_area)
        
        self.btn_go_clothing = QPushButton("Browse Clothing")
        self.btn_go_clothing.setFixedHeight(60)
        self.btn_go_clothing.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_go_clothing.setStyleSheet(self.styles.action_button_style())
        self.btn_go_clothing.clicked.connect(self.request_clothing_view.emit)

        left_layout.addWidget(self.header)
        left_layout.addWidget(title_row)
        left_layout.addStretch()
        left_layout.addWidget(self.room_area, 1)
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
        
        self.main_layout.addWidget(self.preview, 1)
        self.main_layout.addWidget(self.bottom)

    # def refresh_ui(self):
    #     if self.main_layout:
    #         QWidget().setLayout(self.main_layout)
    #     self.init_ui()

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
        if self.sidebar_scroll.width() == 0: self.toggle_sidebar() #opens sidebar if closed
        while self.sidebar_layout.count() > 1: #grabs items from sidebar except title and deltes them one by one to clear
            item = self.sidebar_layout.takeAt(1).widget()
            if item: item.deleteLater()
        for item_data in self.furniture_items.get(category):
            name = item_data[0]
            price = item_data[1]
            path = item_data[2]

            card = FurnitureCard(name, price, path, self, self.styles) #makes card with info from item data
            self.sidebar_layout.addWidget(card,0, Qt.AlignmentFlag.AlignHCenter) #0 is so it doesnt expand

    def update_game_data(self, data):
        self.game_data = data      

    def refresh_page(self, data):
        """Updates UI based on data"""
        self.header.update_money(self.game_data.money)
        self.update_game_data(data)
        

    def attempt_purchase(self, item_name, item_price):
        if self.game_data.money >= item_price:
            self.game_data.money -= item_price
            self.game_data.inventory_furniture.append(item_name)
            self.refresh_page(self.game_data) 
            self.money_changed.emit(self.game_data.money)
            return True
        else:
            lbl = QLabel('Insufficient Funds', self.room_area)
            lbl.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none;background: transparent;")
            lbl.adjustSize()
            lbl.move((self.room_area.width() - lbl.width()) // 2, (self.room_area.height() - lbl.height()) // 2)
            lbl.show()
            QTimer.singleShot(2000, lbl.deleteLater)
            return False
        
    def place_item(self, item_name, image_paths):
        placed_list = self.game_data.placed_furniture
        owned_qty = self.game_data.inventory_furniture.count(item_name)
        placed_qty = sum(1 for item in placed_list if item['name']==item_name)
        
        if owned_qty == 0:
            lbl = QLabel('Item not owned', self.room_area)
            lbl.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none;background: transparent;")
            lbl.adjustSize()
            lbl.move((self.room_area.width() - lbl.width()) // 2, (self.room_area.height() - lbl.height()) // 2)
            lbl.show()
            QTimer.singleShot(2000, lbl.deleteLater)
            return
        
        if placed_qty < owned_qty:
            if self.game_data.placed_furniture:
                current_max_z = max((item.get('z', 0) for item in self.game_data.placed_furniture), default=0)
            new_item_data = {'name': item_name, 'angle_index': 0, 'x':0, 'y':0 , 'z':current_max_z + 1}
            self.game_data.placed_furniture.append(new_item_data)
            item_lbl = DraggableFurniture(self.room_area, image_paths, new_item_data, self)
            item_lbl.setStyleSheet("border: none; background: transparent;")
            item_lbl.show()
            self.refresh_z_order()

            center_x = ((self.room_area.width() - item_lbl.width()) // 2 ) + 100
            center_y = ((self.room_area.height() - item_lbl.height()) // 2) + 100
            item_lbl.move(center_x, center_y)

            new_item_data['x'] = center_x
            new_item_data['y'] = center_y


            self.refresh_page(self.game_data) 
        else:
            lbl = QLabel(f'All {item_name}s placed', self.room_area)
            lbl.setStyleSheet(f"color: red; font-size: 24px; font-weight: bold; border: none; background: transparent;")
            lbl.adjustSize()
            lbl.move((self.room_area.width() - lbl.width()) // 2, (self.room_area.height() - lbl.height()) // 2)
            lbl.show()
            QTimer.singleShot(2000, lbl.deleteLater)
    
    def load_item_image(self):
        '''Looks inside the assets folder for images named Category_Item Name_Price.png in other words gets our info from the image names'''
        assets_folder = "assets"
        data = {}
        grouped_items = {} # so more than 1 item with same name but different rotation can be grouped

        if not os.path.exists(assets_folder):
            print("Assets folder not found.")
            return {} #i make it return empty dict if folder not found so it doesnt crash and can loop thru
        
        valid_file_types = ('.png')
        
        for filename in os.listdir(assets_folder):
            if filename.lower().endswith(valid_file_types):
                #we split by _ to get category, name, price from image name
                name_no_extension = os.path.splitext(filename)[0] #we remove .png first
                parts = name_no_extension.split('_')

                if len(parts) >= 4 and parts[-1].isdigit() and len(parts[-1])==1 and parts[-2].isdigit():
                    category = parts[0]
                    try: price = int(parts[-2])
                    except ValueError: price = 0
                    name = ' '.join(parts[1:-2])
                elif len(parts) >= 3:
                    category = parts[0]
                    try: price = int(parts[-1])
                    except ValueError: price = 0
                    name = ' '.join(parts[1:-1])
                else:
                    continue

                if 'Floor' in name or 'Wall' in name:
                    continue

                key = (category, name, price)
                full_path = os.path.join(assets_folder, filename) #we use it in card and preview later later

                if key not in grouped_items: 
                    grouped_items[key] = []
                grouped_items[key].append(full_path)

        for (cat, name, price), paths in grouped_items.items():
            paths.sort() #sort to have consistent order or rotations if i label them right
            if cat not in data:
                data[cat] = []
            data[cat].append((name, price, paths))

        return data  
     
    def save_layout(self):
        self.request_save_layout.emit(self.game_data.inventory_furniture, self.game_data.placed_furniture)    

    def load_layout(self, data=None):
        
        placed_data = data
        placed_data.sort(key=lambda x: x.get('z',0))

        for item_data in placed_data:
            name = item_data['name']
            image_paths = []
            for category, items in self.furniture_items.items():
                for name,price,paths in items:
                    if name == item_data['name']:
                        image_paths = paths
                        break
                if image_paths:
                    break
            if not image_paths:
                image_paths = self.get_specific_item_images(item_data['name'])

            if image_paths:
                item_lbl = DraggableFurniture(self.room_area, image_paths, item_data, self)
                item_lbl.show()
    
    def refresh_z_order(self):
        """restacks stuff based on the z index"""
        widgets = self.room_area.findChildren(DraggableFurniture)
        sorted_widgets = sorted(widgets, key=lambda w: w.item_data.get('z',0))
        for w in sorted_widgets:
            w.raise_()

    def get_specific_item_images(self, item_name):
        ''' Ik the names crazy, it finds images that are hidden from the store like the floors and walls so it can have the base'''
        assets_folder = 'assets'
        paths = []

        if not os.path.exists(assets_folder): return []

        for filename in os.listdir(assets_folder):
            if item_name in filename and filename.endswith('.png'):
                paths.append(os.path.join(assets_folder, filename))
        
        paths.sort()
        return paths                 
    
class DraggableFurniture(QLabel):
    def __init__(self, parent, image_paths, item_data, main_view):
        super().__init__(parent)
        self.image_paths = image_paths #all the images for rotation
        self.item_data = item_data
        self.angle_index = self.item_data.get('angle_index', 0)
        self.drag_start_position = None
        self.parent_view = main_view
        self.scale_factor = 0.8

        self.is_locked = "Floor" in self.item_data['name'] or "Wall" in self.item_data['name']
        if 'z' not in self.item_data:self.item_data['z'] = 0

        if not self.is_locked:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


        self.setStyleSheet("border: none; background: transparent;")

        self.update_image()

        if 'x' in self.item_data and 'y' in self.item_data:
            self.move(self.item_data['x'], self.item_data['y'])


    def update_image(self):
        if not self.image_paths: return #no images ould crash app
        current_image_path = self.image_paths[self.angle_index]

        if os.path.exists(current_image_path):
            pix = QPixmap(current_image_path)
            new_w = int(pix.width()*self.scale_factor)
            new_h = int(pix.height()*self.scale_factor)
            self.setFixedSize(new_w, new_h)
            self.setPixmap(pix.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def rotate(self):
        if len(self.image_paths) > 1:
            self.angle_index = (self.angle_index + 1) % len(self.image_paths)
            self.item_data['angle_index'] = self.angle_index
            self.update_image()

    def mousePressEvent(self, event):
        if self.is_locked: return
        self.setFocus()
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        elif event.button() == Qt.MouseButton.RightButton:
            self.rotate()
    
    def mouseMoveEvent(self, event):
        if self.is_locked: return
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_start_position:
            delta = event.pos() - self.drag_start_position
            target_pos = self.pos() + delta
            

            parent_rect = self.parentWidget()
            max_x = parent_rect.width() - self.width()
            max_y = parent_rect.height() - self.height()

            safex = max(0, min(target_pos.x(), max_x))
            safey = max(0, min(target_pos.y(), max_y))
            self.move(safex, safey)

            #tosave position
            self.item_data['x'] = safex
            self.item_data['y'] = safey

    def mouseReleaseEvent(self, event):
        if self.is_locked: return
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_start_position = None

    def mouseDoubleClickEvent(self, event):
        if self.is_locked: return
        if event.button() == Qt.MouseButton.LeftButton:
            siblings = self.parentWidget().findChildren(DraggableFurniture)
            current_max_z = 0
            for sib in siblings:
                z= sib.item_data.get('z',0)
                if z > current_max_z:
                    current_max_z = z
            
            self.item_data['z']= current_max_z + 1
            self.raise_()

    def delete_item(self):
        if self.item_data in self.parent_view.game_data.placed_furniture:
            self.parent_view.game_data.placed_furniture.remove(self.item_data)
            self.deleteLater()

    def keyPressEvent(self, event):
        if self.is_locked:return
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self.delete_item()
