from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time


class Worker(QObject):
    finished = pyqtSignal()
    timeProgress = pyqtSignal(float)

    def __init__(self, time_limit: int) -> None:
        super().__init__()
        self.time_limit = time_limit
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False

    @pyqtSlot()
    def timeCounter(self) -> None:
        start_time = time.time()
        end_time = self.time_limit*60
        while (time.time() - start_time) < end_time and self.is_running:
            time.sleep(0.5)
            self.timeProgress.emit((time.time() - start_time) / 60)

        self.finished.emit()