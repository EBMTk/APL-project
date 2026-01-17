import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QCheckBox, QSlider, QLabel, 
                             QCalendarWidget, QTimeEdit, QStackedWidget, 
                             QApplication, QMainWindow, QSizePolicy, QDialog)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal, QSize, QPropertyAnimation, QPoint
from PyQt6.QtGui import QTextCharFormat, QColor, QFont, QIcon
from task_handler import ai_engine

#Task Data Container
class TaskSpecifications():
    def __init__(self, name, date_due, time_due, deadline, subdivisions=0, uuid=1):
        self.uuid = uuid
        self.name = name
        self.subdivisions = subdivisions
        self.deadline = deadline
        self.date_due = date_due
        self.time_due = time_due

        difficulty = ai_engine.get_task_diff(self.name)
        self.reward = difficulty*10

        self.subtasks = 0
        if self.subdivisions:
            self.subtasks = ai_engine.get_subtask_list(self.name, self.subdivisions)

class TaskEntryWidget(QWidget):
    #Signal
    request_main_page = pyqtSignal()
    task_ready_signal = pyqtSignal(object)

    def __init__(self, styles, parent=None):
        super().__init__(parent)
        self.styles = styles
        
        #widgit creation
        self.input_home_pos = None

        self.setStyleSheet(f'background-color: {self.styles.col_primary};')
        
        self.layout_container = QVBoxLayout(self)
        self.view_stack = QStackedWidget()
        self.layout_container.addWidget(self.view_stack)

        self.fnc_setup_main_view()
        self.fnc_setup_time_view()
        self.fnc_setup_date_view()

        self.view_stack.setCurrentIndex(0)

    def fnc_setup_main_view(self):
        view_page = QWidget()
        page_layout = QVBoxLayout(view_page)
        page_layout.setContentsMargins(5,5,5,5)
        page_layout.setSpacing(20)
        page_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        # Top Navigation
        top_nav_bar = QHBoxLayout()
        top_nav_bar.setSpacing(5)

        self.btn_return_home = QPushButton('🏠︎')
        self.btn_return_home.setFixedSize(40, 40)
        self.btn_return_home.clicked.connect(lambda: self.request_main_page.emit())

        self.task_description_input = QLineEdit()
        self.task_description_input.setPlaceholderText('Enter Task Here...')
        self.task_description_input.setFixedHeight(35)
        self.task_description_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.task_description_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.styles.col_secondary};
                border: 2px solid {self.styles.col_border};
                border-radius: 10px;
                padding: 5px;
                color: {self.styles.col_text};
            }}
        """)

        self.btn_add_task = QPushButton('+')
        self.btn_add_task.setFixedSize(40, 40)
        self.btn_add_task.setStyleSheet(self.styles.action_button_style())
        self.btn_add_task.clicked.connect(self.fnc_emit_task_data)

        top_nav_bar.addWidget(self.btn_return_home)
        top_nav_bar.addWidget(self.task_description_input)
        top_nav_bar.addWidget(self.btn_add_task)
        page_layout.addLayout(top_nav_bar)

        # Split Task Controls
        self.chk_enable_split = QCheckBox('Split Task')
        self.chk_enable_split.setStyleSheet(f"color: {self.styles.col_text}; font-weight: bold;")
        self.chk_enable_split.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.sld_subtask_level = QSlider(Qt.Orientation.Horizontal)
        self.sld_subtask_level.setRange(2, 5)
        self.sld_subtask_level.setEnabled(False)
        self.sld_subtask_level.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.lbl_subtask_count = QLabel('2')
        self.lbl_subtask_count.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.chk_enable_split.toggled.connect(self.sld_subtask_level.setEnabled)
        self.sld_subtask_level.valueChanged.connect(lambda val: self.lbl_subtask_count.setText(str(val)))

        split_control_row = QHBoxLayout()
        self.chk_enable_split.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.sld_subtask_level.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_subtask_count.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        split_control_row.setContentsMargins(0,0,0,0)
        split_control_row.setSpacing(5)
        split_control_row.addWidget(self.chk_enable_split)
        split_control_row.addWidget(self.sld_subtask_level)
        split_control_row.addWidget(self.lbl_subtask_count)
        page_layout.addLayout(split_control_row)

        # Deadline row
        self.chk_use_deadline = QCheckBox('Set Deadline')
        self.chk_use_deadline.setStyleSheet(f"color: {self.styles.col_text}; font-weight: bold;")
        self.chk_use_deadline.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        deadline_row = QHBoxLayout()
        deadline_row.setSpacing(2)
        deadline_row.addWidget(self.chk_use_deadline)
        page_layout.addLayout(deadline_row)

        # Icon Buttons (Clock / Calendar)
        self.image_button_row = QHBoxLayout()
        img_btn_style = 'QPushButton { border: none; background: transparent; padding: 0px; }'

        self.btn_clock_display = QPushButton()
        self.btn_clock_display.setIcon(QIcon('clock_icon.png'))
        self.btn_clock_display.clicked.connect(self.fnc_show_time_popup)
        self.btn_clock_display.setStyleSheet(img_btn_style)

        self.btn_calendar_display = QPushButton()
        self.btn_calendar_display.setIcon(QIcon('calendar_icon.png'))
        self.btn_calendar_display.clicked.connect(self.fnc_show_calendar_popup)
        self.btn_calendar_display.setStyleSheet(img_btn_style)

        self.image_button_row.addWidget(self.btn_clock_display)
        self.image_button_row.addWidget(self.btn_calendar_display)
        page_layout.addLayout(self.image_button_row)

        self.btn_clock_display.setIconSize(QSize(100,100))
        self.btn_calendar_display.setIconSize(QSize(100,100))

        self.view_stack.addWidget(view_page)


        #time page
    def fnc_setup_time_view(self):
        view_page = QWidget()
        page_layout = QVBoxLayout(view_page)

        header_layout = QHBoxLayout()
        btn_back_to_main = QPushButton('<')
        self.btn_return_home.setStyleSheet(self.styles.button_style())
        btn_back_to_main.setFixedSize(40, 40)
        btn_back_to_main.clicked.connect(lambda: self.view_stack.setCurrentIndex(0))
        header_layout.addWidget(btn_back_to_main)
        header_layout.addStretch()
        page_layout.addLayout(header_layout)

        page_layout.addStretch()
        self.time_selector_widget = QTimeEdit()
        self.time_selector_widget.setTime(QTime.currentTime())
        self.time_selector_widget.setFixedSize(150, 40)
        page_layout.addWidget(self.time_selector_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addStretch()

        self.view_stack.addWidget(view_page)

        self.time_selector_widget.setStyleSheet(f"""
            QTimeEdit {{
                background-color: {self.styles.col_secondary};
                color: {self.styles.col_text};
                border: 2px solid {self.styles.col_border};
                border-radius: 10px;
                font-size: 20px;
            }}
        """)

        #date page
    def fnc_setup_date_view(self):
        view_page = QWidget()
        page_layout = QVBoxLayout(view_page)

        header_layout = QHBoxLayout()
        btn_back_to_main = QPushButton('<')
        btn_back_to_main.setFixedSize(40, 40)
        btn_back_to_main.clicked.connect(lambda: self.view_stack.setCurrentIndex(0))
        header_layout.addWidget(btn_back_to_main)
        header_layout.addStretch()
        page_layout.addLayout(header_layout)

        self.date_calendar_widget = QCalendarWidget()
        self.date_calendar_widget.clicked.connect(self.fnc_mark_date_red)
        page_layout.addWidget(self.date_calendar_widget)

        self.view_stack.addWidget(view_page)

        self.date_calendar_widget.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                background-color: {self.styles.col_secondary};
                color: {self.styles.col_text};
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                selection-background-color: {self.styles.col_hover};
                selection-color: {self.styles.col_primary};
            }}
        """)

    def fnc_mark_date_red(self):
        self.date_calendar_widget.setDateTextFormat(QDate(), QTextCharFormat())
        red_format = QTextCharFormat()
        red_format.setForeground(QColor('red'))
        red_format.setFontWeight(QFont.Weight.Bold)
        current_selection = self.date_calendar_widget.selectedDate()
        self.date_calendar_widget.setDateTextFormat(current_selection, red_format)

    #shaking like a stripa on a pole what whaaaat
    def fnc_shake_input(self):
        # makes it so we know the original place of the bar so it returns to place
        if self.input_home_pos is None:
            self.input_home_pos = self.task_description_input.pos()
        
        self.animation = QPropertyAnimation(self.task_description_input, b'pos')
        self.animation.setDuration(250) 
        
        #Shake it off oh baby shake it offfff
        self.animation.setKeyValueAt(0, self.input_home_pos)
        self.animation.setKeyValueAt(0.2, self.input_home_pos + QPoint(-7, 0))
        self.animation.setKeyValueAt(0.4, self.input_home_pos + QPoint(7, 0))
        self.animation.setKeyValueAt(0.6, self.input_home_pos + QPoint(-7, 0))
        self.animation.setKeyValueAt(0.8, self.input_home_pos + QPoint(7, 0))
        self.animation.setKeyValueAt(1, self.input_home_pos)
        
        self.animation.start()

    #makes object acording to check boxes
    def fnc_emit_task_data(self):
        desc = self.task_description_input.text().strip()
        
        if not desc:
            self.fnc_shake_input() 
            return

        split_val = self.sld_subtask_level.value() if self.chk_enable_split.isChecked() else 0
        
        date_val = None
        time_val = None

        deadline = 0
        if self.chk_use_deadline.isChecked():
            deadline = 1
            date_val = self.date_calendar_widget.selectedDate().toString('yyyy-MM-dd')
            time_val = self.time_selector_widget.time().toString('HH:mm')

        #object stuff
        new_task = TaskSpecifications(desc, date_val, time_val, deadline, subdivisions=split_val, uuid=self.current_uuid)
        self.task_ready_signal.emit(new_task)
        self.fnc_reset_ui_inputs()

    #Reset UI and Reset values after clicking +
    def fnc_reset_ui_inputs(self):
        self.task_description_input.clear()
        self.chk_enable_split.setChecked(False)
        self.chk_use_deadline.setChecked(False)
        self.sld_subtask_level.setValue(2)
        self.lbl_subtask_count.setText('2')
        self.lbl_subtask_count.setStyleSheet(f"color: {self.styles.col_text};")
        self.date_calendar_widget.setSelectedDate(QDate.currentDate())
        self.date_calendar_widget.setDateTextFormat(QDate(), QTextCharFormat())
        self.time_selector_widget.setTime(QTime.currentTime())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Clear the home position on resize so the shake adapts to new window size at first it kept shiting left lol shit was too funny
        self.input_home_pos = None
        
        scaled_dim = int(min(self.width() * 5, self.height() * 5))
        new_icon_size = QSize(scaled_dim, scaled_dim)
        self.btn_clock_display.setIconSize(new_icon_size)
        self.btn_calendar_display.setIconSize(new_icon_size)
        self.btn_clock_display.setStyleSheet(f"""
            QPushButton {{
                border: 3px solid {self.styles.col_border};   
                border-radius: 25px;                          
                background-color: {self.styles.col_secondary}; 
                padding: 10px;
            }}
            QPushButton:hover {{
                border: 3px solid {self.styles.col_hover};
            }}
            """)
        self.btn_calendar_display.setStyleSheet(f"""
            QPushButton {{
                border: 3px solid {self.styles.col_border};   
                border-radius: 25px;                          
                background-color: {self.styles.col_secondary}; 
                padding: 10px;
            }}
            QPushButton:hover {{
                border: 3px solid {self.styles.col_hover};
            }}
            """)

    def fnc_show_time_popup(self):
        popup = QDialog(self)
        popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        popup.setStyleSheet(f"background-color: {self.styles.col_primary}; border: 1px solid {self.styles.col_border};")
        
        layout = QVBoxLayout(popup)
        
        time_widget = QTimeEdit()
        time_widget.setTime(self.time_selector_widget.time())
        time_widget.setFixedSize(200, 50)
        
        # FIX: Ensure it accepts wheel and arrow keys immediately
        time_widget.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        time_widget.setReadOnly(False)
        time_widget.setButtonSymbols(QTimeEdit.ButtonSymbols.UpDownArrows)

        # FIX: Styling for the internal buttons (Arrows)
        # If the background is too dark, the arrows might be invisible or unclickable
        time_widget.setStyleSheet(f"""
            QTimeEdit {{
                background-color: {self.styles.col_secondary};
                color: {self.styles.col_text};
                border: 2px solid {self.styles.col_border};
                border-radius: 10px;
                padding: 5px;
                font-size: 18px;
            }}
            QTimeEdit::up-button, QTimeEdit::down-button {{
                width: 30px;
                background: {self.styles.col_primary}; /* Lighter background for the buttons */
                border-left: 1px solid {self.styles.col_border};
            }}
            /* Small horizontal line to separate the two buttons */
            QTimeEdit::up-button {{
                border-bottom: 0.5px solid {self.styles.col_border};
                border-top-right-radius: 8px;
            }}
            QTimeEdit::down-button {{
                border-top: 0.5px solid {self.styles.col_border};
                border-bottom-right-radius: 8px;
            }}
            /* Arrows set to the dark text color so they are visible on the light background */
            QTimeEdit::up-arrow {{
                image: none;
                width: 0; height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid {self.styles.col_text};
            }}
            QTimeEdit::down-arrow {{
                image: none;
                width: 0; height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.styles.col_text};
            }}
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                background: {self.styles.col_hover};
            }}
        """)
        
        layout.addWidget(time_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        
        # Apply your existing styles to popup buttons
        btn_ok.setStyleSheet(self.styles.button_style())
        btn_cancel.setStyleSheet(self.styles.button_style())
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        btn_ok.clicked.connect(lambda: (
            self.time_selector_widget.setTime(time_widget.time()), 
            popup.accept()
        ))
        btn_cancel.clicked.connect(popup.reject)
        
        popup.adjustSize()
        
        # Center on parent
        parent_rect = self.rect()
        popup.move(
            self.mapToGlobal(parent_rect.center()) - popup.rect().center()
        )
        
        popup.exec()




    def fnc_show_calendar_popup(self):
        popup = QDialog(self)
        popup.setWindowFlags(Qt.WindowType.Popup)
        
        layout = QVBoxLayout(popup)
        
        calendar = QCalendarWidget()
        calendar.setSelectedDate(self.date_calendar_widget.selectedDate())  # current selection
        calendar.setFixedSize(400, 300)
        calendar.setStyleSheet(f"""
            QCalendarWidget {{
                border: 2px solid {self.styles.col_border};
                border-radius: 10px;
            }}
            QCalendarWidget QToolButton {{
                color: {self.styles.col_text};
            }}
            QCalendarWidget QSpinBox {{
                color: {self.styles.col_text};
            }}
        """)
        layout.addWidget(calendar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        # Button behavior
        btn_ok.clicked.connect(lambda: (
            self.date_calendar_widget.setSelectedDate(calendar.selectedDate()),
            popup.accept()
        ))
        btn_cancel.clicked.connect(popup.reject)
        
        popup.adjustSize()
        
        # Center on parent
        parent_rect = self.rect()
        popup.move(
            self.mapToGlobal(parent_rect.center()) - popup.rect().center()
        )
        
        popup.exec()

    def update_uuid(self, uuid):
        self.current_uuid = uuid