import sys

from fbs_runtime.application_context import ApplicationContext
from fbs_runtime.platform import is_mac, is_windows
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QTextStream

from main_window import PomodoroWindow


class AppContext(ApplicationContext):           # 1. Subclass ApplicationContext

    @property
    def app_icon(self):
        """
        The app icon. Not available on Mac because app icons are handled by the
        OS there.
        """
        if not is_mac():
            return QIcon(self.get_resource('Icon.ico'))

    def run(self):                              # 2. Implement run()
        file = QFile(self.get_resource('darkStyle.qss'))
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        if not getattr(sys, 'frozen', False):
            stylesheet = stylesheet.replace('dark/', 'src/main/resources/base/dark/')
        self.app.setStyleSheet(stylesheet)
        window = PomodoroWindow(self.app)
        window.show()
        return self.app.exec_()                 # 3. End run() with this line

if __name__ == '__main__':
    appctxt = AppContext()                      # 4. Instantiate the subclass
    exit_code = appctxt.run()                   # 5. Invoke run()
    sys.exit(exit_code)
