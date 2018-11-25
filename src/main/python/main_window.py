import os
import time

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QBrush, QColor, QFont, QIcon, QPalette
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QPushButton, QSpinBox,
                             QSystemTrayIcon, QTextEdit, QVBoxLayout, QWidget)

import worker
from constants import (APPLICATION_NAME, FONT_NAME, FONT_SIZE,
                       HORIZONTAL_SPACING, START_BUTTON_LABEL,
                       STOP_BUTTON_LABEL, TIME_INPUT_LABEL, TIME_LIMIT_MAXIMUM,
                       TIME_LIMIT_MINIMUM, VERTICAL_SPACING, WINDOW_SIZE)
from progressbar import QRoundProgressBar


class PomodoroWindow(QMainWindow):

    def __init__(self, app) -> None:
        super().__init__()
        self.app = app
        self.time_limit = 20
        self.timer_started = False
        self.stopped_forcefully = False
        self.init_UI()

    def init_UI(self) -> None:
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(*WINDOW_SIZE)
        self.setFixedSize(self.size())

        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(VERTICAL_SPACING)
        self.grid.setHorizontalSpacing(HORIZONTAL_SPACING)

        self.create_time_limit_input()
        self.create_progress_bar()
        self.create_start_button()

        centralWidget = QWidget()
        centralWidget.setLayout(self.grid)
        self.setCentralWidget(centralWidget)

    def create_time_limit_input(self) -> None:
        self.time_limit_label = QLabel(TIME_INPUT_LABEL)
        self.time_limit_label.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Bold))
        self.time_limit_input = QSpinBox()
        self.time_limit_input.setMinimumSize(60, 30)
        self.time_limit_input.setMinimum(TIME_LIMIT_MINIMUM)
        self.time_limit_input.setMaximum(TIME_LIMIT_MAXIMUM)
        self.time_limit_input.setValue(self.time_limit)
        self.time_limit_input.valueChanged.connect(self.time_limit_changed)

        self.grid.addWidget(self.time_limit_label, 1, 0, 1, 2)
        self.grid.addWidget(self.time_limit_input, 1, 2, 1, 2)

    def create_progress_bar(self) -> None:
        hbox = QHBoxLayout()
        self.progress_bar = QRoundProgressBar(end_value=self.time_limit)
        hbox.addWidget(self.progress_bar, 0, Qt.AlignCenter)
        self.grid.addLayout(hbox, 2, 0, 5, 5)

    def create_start_button(self) -> None:
        self.start_button = QPushButton(START_BUTTON_LABEL)
        self.start_button.setFont(QFont(FONT_NAME, FONT_SIZE, QFont.Bold))
        self.start_button.clicked.connect(self.timer_btn_clicked)
        hbox = QHBoxLayout()
        hbox.addWidget(self.start_button, 0, Qt.AlignHCenter)

        self.grid.addLayout(hbox, 7, 0, 1, 5)

    def time_limit_changed(self) -> None:
        self.time_limit = self.time_limit_input.value()
        self.progress_bar.set_range(0, self.time_limit)

    def configure_worker(self) -> None:
        self.timer_worker = worker.Worker(self.time_limit)
        self.timer_thread = QThread()

        self.timer_worker.timeProgress.connect(self.time_progress)
        self.timer_worker.moveToThread(self.timer_thread)
        self.timer_worker.finished.connect(self.timer_ended)
        self.timer_thread.started.connect(self.timer_worker.timeCounter)

    def time_progress(self, time_progressed: float) -> None:
        self.progress_bar.value = time_progressed

    def init_timer(self) -> None:
        self.timer_started = True
        self.configure_worker()

    def stop_timer(self) -> None:
        self.timer_started = False
        self.timer_worker.stop()
        self.timer_thread.quit()

    def timer_btn_clicked(self) -> None:
        if not self.timer_started:
            self.init_timer()
            self.start_button.setDisabled(True)
            self.start_button.setText(STOP_BUTTON_LABEL)
            self.timer_thread.start()
            self.start_button.setEnabled(True)
        else:
            self.stopped_forcefully = True
            self.stop_timer()

    def timer_ended(self) -> None:
        self.start_button.setText(START_BUTTON_LABEL)
        self.stop_timer()
        if not self.stopped_forcefully:
            self.show_notification()
        self.stopped_forcefully = False

    def show_notification(self) -> None:
        system_tray_icon = QSystemTrayIcon(
            QIcon('src/main/icons/Icon.ico'), self)
        system_tray_icon.show()
        text = str(self.time_limit) + \
            ' minutes have passed. ' if self.time_limit > 1 else '1 minutes has passed. '
        system_tray_icon.showMessage('Time Up!', text + 'Take a break!')
