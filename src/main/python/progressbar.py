from collections import namedtuple
from string import Template
from typing import Dict

from PyQt5.QtCore import QPointF, QRectF, Qt, pyqtSlot
from PyQt5.QtGui import (QConicalGradient, QFont, QFontMetricsF, QGradient,
                         QImage, QPainter, QPainterPath, QPaintEvent, QPalette,
                         QPen, QRadialGradient)
from PyQt5.QtWidgets import QWidget

from constants import (DEFAULT_MARGIN, DEFAULT_PEN_WIDTH, FONT_NAME, FONT_SIZE,
                       FULL_ANGLE, POSITION_BOTTOM, POSITION_LEFT,
                       POSITION_RIGHT, POSITION_TOP, PYQT_ANGLE_PRECISION,
                       SIDE_FRACTION)

# A named tuple to define the margin of any widget
Margin = namedtuple('Margin', ['top', 'right', 'bottom', 'left'])


class DrawingPainter(object):
    """A class to attach a with context to QPainter object
    """
    def __init__(self, painter: QPainter, pen: QPen) -> None:
        """Initialise the Context manager, and customise it.

        :param painter: A QPainter object to attach to context manager
        :param pen: A QPen object to customise the painter object.
        """
        self.painter = painter
        self._old_pen = painter.pen()
        self.painter.setPen(pen)

    def __enter__(self) -> QPainter:
        """On entry, return the customised painter object.
        """
        return self.painter

    def __exit__(self, type, value, traceback) -> None:
        """On exit, revert any customisations done on the painter object.
        """
        self.painter.setPen(self._old_pen)


class QRoundProgressBar(QWidget):
    """Custom QWidget to implement a round progress bar.

    :attr: PositionLeft: Left position on the round progressbar in degrees. (180 degrees)
    :attr: PositionTop: Top position on the round progressbar in degrees. (90 degrees)
    :attr: PositionRight:  Right position on the round progressbar in degrees. (0 degrees)
    :attr: PositionBottom: Bottom position on the round progressbar in degrees. (-90 degrees)
    """

    PositionLeft = POSITION_LEFT
    PositionTop = POSITION_TOP
    PositionRight = POSITION_RIGHT
    PositionBottom = POSITION_BOTTOM

    def __init__(self, parent=None, start_value: float = 0, 
                 end_value: float = 100, value: float = 0) -> None:
        """Initialise the round progressbar

        :param parent = None: Parent object for the round progressbar.
        :param start_value = 0: Starting value for the progressbar.
        :param end_value = 0: Ending value for the progressbar.
        :param value = 0: Current value for the progressbar.
        """
        super().__init__(parent)
        self._start_value = start_value
        self._end_value = end_value
        self._value = value
        # Template to display text at the center of progressbar (Eg. 80 / 100)
        self._str_template = Template('$value / $end_value')
        self._font = QFont(FONT_NAME, FONT_SIZE, QFont.Bold)
        self._margin_percent = Margin(top=DEFAULT_MARGIN, right=DEFAULT_MARGIN,
                                      bottom=DEFAULT_MARGIN, left=DEFAULT_MARGIN)
        self._pen_width = DEFAULT_PEN_WIDTH

        self.initUI()

    @property
    def start_value(self) -> float:
        """Starting value for the progressbar.

        getter: Get the starting value of the progressbar.
        setter: Set the starting value of the progressbar.
        """
        return self._start_value

    @start_value.setter
    def start_value(self, val: float) -> None:
        self._start_value = val

    @property
    def end_value(self) -> float:
        """Ending value for the progressbar.

        getter: Get the ending value of the progressbar.
        setter: Set the ending value of the progressbar.
        """
        return self._end_value

    @end_value.setter
    def end_value(self, val: float) -> None:
        self._end_value = val

    def set_range(self, start: float, end: float):
        """Set the starting and the ending value for progressbar.

        :param start: float: Starting value for the progressbar.
        :param end: float: Ending value for the progressbar.
        """
        self._start_value = start
        self._end_value = end
        # After the range is changed, update the UI to reflect changes
        self.update()

    @property
    def value(self) -> float:
        """Current value for the progressbar.

        getter: Get the current value of the progressbar.
        setter: Set the current value of the progressbar.
        """
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value
        # After the value is updated, update the UI to reflect changes
        self.update()

    @property
    def font(self) -> QFont:
        """Font object to be used for the text at the center of progressbar.

        getter: Get the font object used for the text at the center of progressbar.
        setter: Set the font object used for the text at the center of progressbar.
        """
        return self._font

    @font.setter
    def font(self, font: QFont) -> None:
        self._font = font

    @property
    def pen_width(self) -> int:
        """Width of the pen to be used to draw the circles.

        getter: Get the width of the pen used to draw the circles.
        setter: Set the width of the pen used to draw the circles.
        """
        return self._pen_width

    @pen_width.setter
    def pen_width(self, width: int) -> None:
        self._pen_width = width

    def initUI(self) -> None:
        """Set the minimum size of the progressbar
        """
        self.setMinimumSize(200, 200)

    def getAdjustedRect(self) -> QRectF:
        """Returns a rectangle after adding margin to the base rectangle, with same center.
        """
        leftMargin = (self._margin_percent.left * self._side) / 100
        rightmargin = (self._margin_percent.right * self._side) / 100
        topMargin = (self._margin_percent.top * self._side) / 100
        bottomMargin = (self._margin_percent.bottom * self._side) / 100
        adjustedRect = self._baseRect.adjusted(leftMargin, rightmargin,
                                               -topMargin, -bottomMargin)
        return adjustedRect

    def paintEvent(self, event: QPaintEvent) -> None:
        """Update the UI, called regularly by Qt whenever self.update is called.

        :param event: QPaintEvent: QPaint event that is passed to the method by Qt.
        """
        self._painter = QPainter()
        self._painter.begin(self)
        self._painter.setRenderHint(QPainter.TextAntialiasing, True)
        self._painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.drawWidget()
        self._painter.end()

    def drawWidget(self) -> None:
        """Draw the Progressbar and the text at the center.
        """
        size = self.size()
        self._side = SIDE_FRACTION * min(size.width(), size.height())
        self._baseRect = QRectF(0, 0, self._side, self._side)

        self.drawProgressBar()
        self.drawCenterText()

    def drawProgressBar(self) -> None:
        """Draw the round progressbar.
        First a circle is drawn at the center of the available space. Next an arc is drawn depending the current value.
        Angle of arc = (current_value - start_value) / (end_value - start_value) * 360
        """
        adjustedRect = self.getAdjustedRect()
        with DrawingPainter(self._painter, QPen(Qt.green, self._pen_width + 6, Qt.SolidLine, Qt.FlatCap)) as painter:
            painter.drawEllipse(adjustedRect)

        with DrawingPainter(self._painter, QPen(Qt.red, self._pen_width, Qt.SolidLine, Qt.FlatCap)) as painter:
            startAngle = self.PositionTop * PYQT_ANGLE_PRECISION
            endAngle = -int(((self.value - self.start_value) /
                             (self.end_value - self.start_value)) * FULL_ANGLE * PYQT_ANGLE_PRECISION)
            painter.drawArc(adjustedRect, startAngle, endAngle)

    def drawCenterText(self) -> None:
        """Draw text at the center of the Progressbar in the form "current_value / end_value"
        """
        substitution = {'value': str(round(self.value, 2)), 'end_value': str(round(self.end_value, 2))} # type: Dict[str, str]
        text = self._str_template.substitute(substitution)
        self._painter.setFont(self.font)
        self._painter.drawText(self._baseRect, Qt.AlignCenter, text)
