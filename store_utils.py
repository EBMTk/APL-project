from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal

### UNIVERSAL_STYLES ###
class UniversalStyles:
    def __init__(self, primary, secondary, border, hover, text, scroll, scroll_hover):
        self.col_primary = primary
        self.col_secondary = secondary
        self.col_border = border
        self.col_hover = hover
        self.col_text = text
        self.col_scroll = scroll
        self.col_scroll_hover = scroll_hover
        
    def header_button_style(self):
        return f"""
        QPushButton {{
            background-color: {self.col_primary};
            border: 2px solid {self.col_border};
            font-size: 20px;
            color: {self.col_text};
        }}
        QPushButton:hover {{
            background-color: {self.col_hover};
        }}
        """
    def money_label_style(self):
        return f"""
        QLabel {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.col_text};
        }}
        """

    def frame_style(self):
        return f"""
        QFrame {{
            background-color: {self.col_secondary};
            border: 1.5px solid {self.col_border};
            border-radius: 25px;
        }}
        """

    def action_button_style(self):
        return f"""
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
        """

    def scrollbar_style(self):
        return f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 14px; margin: 10px 0px; }}
        QScrollBar::handle:vertical {{ background: {self.col_scroll}; min-height: 30px; border-radius: 7px; }}
        QScrollBar::handle:vertical:hover {{ background: {self.col_scroll_hover}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

        QScrollBar:horizontal {{ background: transparent; height: 14px; margin: 0px 10px; border: none; }}
        QScrollBar::handle:horizontal {{ background: {self.col_scroll}; min-width: 30px; border-radius: 7px; }}
        QScrollBar::handle:horizontal:hover {{ background: {self.col_scroll_hover}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: none; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
        """

### STORE_HEADER ###
class store_header(QWidget):
    home_clicked = pyqtSignal()

    def __init__(self, styles):
        super().__init__()
        self.styles = styles 
        self.setStyleSheet("border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.setSpacing(15) 

        self.btn_home = QPushButton("🏠︎") 
        self.btn_home.setFixedSize(50, 50) 
        self.btn_home.setCursor(Qt.CursorShape.PointingHandCursor) 
        self.btn_home.setToolTip("Home") 
        self.btn_home.setStyleSheet(self.styles.header_button_style()) 
        self.btn_home.clicked.connect(self.home_clicked.emit) 

        self.lbl_money = QLabel("$0") #from the database
        self.lbl_money.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.lbl_money.setFixedSize(150, 50) 
        self.lbl_money.setStyleSheet(f"""
            background-color: {self.styles.col_secondary};
            border: 2.5px solid {self.styles.col_text};
            border-radius: 12px;
            font-weight: 900;
            font-size: 18px;
            color: {self.styles.col_text};
        """) 
        layout.addWidget(self.btn_home) 
        layout.addStretch() 
        layout.addWidget(self.lbl_money) 

    def update_money(self, amount):
        self.lbl_money.setText(f"${amount}")

### HORIZONTAL SCROLL AREA ###
class HorizontalScrollArea(QScrollArea):
    def wheelEvent(self, event):
      """Enable horizontal scrolling with mouse wheel"""
      delta = event.angleDelta().y()
      if delta != 0:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()
      else:
            return super().wheelEvent(event)