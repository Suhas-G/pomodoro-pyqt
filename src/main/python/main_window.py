import time
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QBrush, QColor, QPalette

from qroundprogressbar import QRoundProgressBar
import worker

class PomodoroWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.time_limit = 20
        self.timer_started = False
        self.configure_worker()
        self.init_UI()
                

    def init_UI(self):
        self.setWindowTitle("Pomodoro")
        self.resize(450, 350)
        self.setFixedSize(self.size())

        self.grid = QGridLayout()
        
        self.grid.setVerticalSpacing(30)
        self.grid.setHorizontalSpacing(10)

        self.create_time_limit_input()
        self.create_progress_bar()
        self.create_start_button()

        

        centralWidget = QWidget()
        centralWidget.setLayout(self.grid)
        self.setCentralWidget(centralWidget)

    def create_time_limit_input(self):
        self.time_limit_label = QLabel('Time Limit')
        self.time_limit_input = QSpinBox()
        self.time_limit_input.setMaximum(120)
        self.time_limit_input.setValue(self.time_limit)
        self.time_limit_input.valueChanged.connect(self.time_limit_changed)

        self.grid.addWidget(self.time_limit_label, 1, 0)
        self.grid.addWidget(self.time_limit_input, 1, 1)

    def create_progress_bar(self):

        self.progress_bar = QRoundProgressBar()
        self.progress_bar.setBarStyle(QRoundProgressBar.BarStyle.DONUT)
        self.progress_bar.setDecimals(1)
        self.progress_bar.setFormat('%v')
        self.progress_bar.setRange(0, self.time_limit)
        self.progress_bar.setValue(0)
        self.progress_bar.setDataPenWidth(0.5)

        # style accordingly via palette
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush)
        self.progress_bar.setPalette(palette)

        self.grid.addWidget(self.progress_bar, 2, 1, 5, 3)

    def create_start_button(self):
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.timer_btn_clicked)
        hbox = QHBoxLayout()
        hbox.addWidget(self.start_button, 0, Qt.AlignHCenter)

        self.grid.addLayout(hbox, 7, 0, 1, 5)

    def time_limit_changed(self):
        self.time_limit = self.time_limit_input.value()
        self.progress_bar.setRange(0, self.time_limit)
        print(self.time_limit, flush=True)

    def configure_worker(self):
        self.timer_worker = worker.Worker(self.time_limit)
        self.timer_thread = QThread()

        self.timer_worker.timeProgress.connect(self.time_progress)
        self.timer_worker.moveToThread(self.timer_thread)
        self.timer_worker.finished.connect(self.timer_ended)
        self.timer_thread.started.connect(self.timer_worker.timeCounter)

    def time_progress(self, time_progressed):
        self.progress_bar.setValue(time_progressed)

    def timer_btn_clicked(self):
        if not self.timer_started:
            self.timer_started = True
            self.start_button.setText('Stop')
            self.timer_thread.start()
            print('Timer started', flush=True)
        else:
            self.timer_worker.finished.emit()

    def timer_ended(self):
        self.start_button.setText('Start')
        self.timer_thread.quit()