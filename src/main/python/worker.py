from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time


class Worker(QObject):
    finished = pyqtSignal()
    timeProgress = pyqtSignal(float)

    def __init__(self, time_limit: int):
        super().__init__()
        self.time_limit = time_limit


    @pyqtSlot()
    def timeCounter(self):
        for i in range(0, self.time_limit*60):
            time.sleep(1)
            self.timeProgress.emit(i / 60)

        self.finished.emit()