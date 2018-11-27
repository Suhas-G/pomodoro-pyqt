from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import time


class Worker(QObject):
    """Worker object, that runs on a separate thread from the main thread.

    :attr: finished: A PyQt signal to indicate the thread has finished.
    :attr: timeProgress: A PyQt signal to periodically indicate how much time has passed.
    """
    finished = pyqtSignal()
    timeProgress = pyqtSignal(float)

    def __init__(self, time_limit: int) -> None:
        """Initialise the timer.

        :param: time_limit: Time limit for the timer thread.
        """
        super().__init__()
        self.time_limit = time_limit
        self.is_running = True

    def stop(self) -> None:
        """Stop the thread by setting is_running False 
        """
        self.is_running = False

    @pyqtSlot()
    def timeCounter(self) -> None:
        """Run a counter, till the timer is stopped or reaches the time limit.

        Emit a timeProgress signal approximately every 0.5 seconds.
        Emit a finished signal after it has finished.
        """
        start_time = time.time()
        end_time = self.time_limit*60
        while (time.time() - start_time) < end_time and self.is_running:
            time.sleep(0.5)
            self.timeProgress.emit((time.time() - start_time) / 60)

        self.finished.emit()