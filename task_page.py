import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QCheckBox, QSlider, QLabel, 
                             QCalendarWidget, QTimeEdit, QStackedWidget, 
                             QApplication, QMainWindow)
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

    def __init__(self, parent=None):
        super().__init__(parent)
        
        #widgit creation
        self.input_home_pos = None
        
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

        #Top Navigation
        top_nav_bar = QHBoxLayout()
        
        self.btn_return_home = QPushButton('🏠︎')
        self.btn_return_home.setFixedSize(40, 40)
        self.btn_return_home.clicked.connect(lambda: self.request_main_page.emit())
        
        self.task_description_input = QLineEdit()
        self.task_description_input.setPlaceholderText('Enter Task Here...')
        self.task_description_input.setFixedHeight(40)
        
        self.btn_add_task = QPushButton('+')
        self.btn_add_task.setFixedSize(40, 40)
        self.btn_add_task.clicked.connect(self.fnc_emit_task_data)

        top_nav_bar.addWidget(self.btn_return_home)
        top_nav_bar.addWidget(self.task_description_input)
        top_nav_bar.addWidget(self.btn_add_task)
        page_layout.addLayout(top_nav_bar)

        #Split Task Controls
        split_control_row = QHBoxLayout()
        self.chk_enable_split = QCheckBox('Split Task')
        
        self.sld_subtask_level = QSlider(Qt.Orientation.Horizontal)
        self.sld_subtask_level.setRange(2, 5)
        self.sld_subtask_level.setEnabled(False)
        self.lbl_subtask_count = QLabel('2')

        self.chk_enable_split.toggled.connect(self.sld_subtask_level.setEnabled)
        self.sld_subtask_level.valueChanged.connect(lambda val: self.lbl_subtask_count.setText(str(val)))

        split_control_row.addWidget(self.chk_enable_split)
        split_control_row.addWidget(self.sld_subtask_level)
        split_control_row.addWidget(self.lbl_subtask_count)
        page_layout.addLayout(split_control_row)

        #Deadline check box
        deadline_row = QHBoxLayout()
        self.chk_use_deadline = QCheckBox('Set Deadline')
        deadline_row.addWidget(self.chk_use_deadline)
        page_layout.addLayout(deadline_row)

        #Section: Icon Buttons
        self.image_button_row = QHBoxLayout()
        img_btn_style = 'QPushButton { border: none; background: transparent; padding: 0px; }'
        
        self.btn_clock_display = QPushButton()
        self.btn_clock_display.setIcon(QIcon('clock_icon.png')) 
        self.btn_clock_display.clicked.connect(lambda: self.view_stack.setCurrentIndex(1))
        self.btn_clock_display.setStyleSheet(img_btn_style)

        self.btn_calendar_display = QPushButton()
        self.btn_calendar_display.setIcon(QIcon('calendar_icon.png'))
        self.btn_calendar_display.clicked.connect(lambda: self.view_stack.setCurrentIndex(2))
        self.btn_calendar_display.setStyleSheet(img_btn_style)

        self.image_button_row.addWidget(self.btn_clock_display)
        self.image_button_row.addWidget(self.btn_calendar_display)
        page_layout.addLayout(self.image_button_row)

        self.view_stack.addWidget(view_page)

        #time page
    def fnc_setup_time_view(self):
        view_page = QWidget()
        page_layout = QVBoxLayout(view_page)

        header_layout = QHBoxLayout()
        btn_back_to_main = QPushButton('<')
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
        self.date_calendar_widget.setSelectedDate(QDate.currentDate())
        self.date_calendar_widget.setDateTextFormat(QDate(), QTextCharFormat())
        self.time_selector_widget.setTime(QTime.currentTime())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Clear the home position on resize so the shake adapts to new window size at first it kept shiting left lol shit was too funny
        self.input_home_pos = None
        
        scaled_dim = min(self.width() // 2, self.height() // 2)
        new_icon_size = QSize(scaled_dim, scaled_dim)
        self.btn_clock_display.setIconSize(new_icon_size)
        self.btn_calendar_display.setIconSize(new_icon_size)
    
    def update_uuid(self, uuid):
        self.current_uuid = uuid