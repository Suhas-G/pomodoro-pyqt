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

Margin = namedtuple('Margin', ['top', 'right', 'bottom', 'left'])


class DrawingPainter(object):
    def __init__(self, painter: QPainter, pen: QPen) -> None:
        self.painter = painter
        self._old_pen = painter.pen()
        self.painter.setPen(pen)

    def __enter__(self) -> QPainter:
        return self.painter

    def __exit__(self, type, value, traceback) -> None:
        self.painter.setPen(self._old_pen)


class QRoundProgressBar(QWidget):

    PositionLeft = POSITION_LEFT
    PositionTop = POSITION_TOP
    PositionRight = POSITION_RIGHT
    PositionBottom = POSITION_BOTTOM

    def __init__(self, parent=None, start_value: float = 0, 
                 end_value: float = 100, value: float = 0) -> None:
        super().__init__(parent)
        self._start_value = start_value
        self._end_value = end_value
        self._value = value
        self._str_template = Template('$value / $end_value')
        self._font = QFont(FONT_NAME, FONT_SIZE, QFont.Bold)
        self._margin_percent = Margin(top=DEFAULT_MARGIN, right=DEFAULT_MARGIN,
                                      bottom=DEFAULT_MARGIN, left=DEFAULT_MARGIN)
        self._pen_width = DEFAULT_PEN_WIDTH

        self.initUI()

    @property
    def start_value(self) -> float:
        return self._start_value

    @start_value.setter
    def start_value(self, val: float) -> None:
        self._start_value = val

    @property
    def end_value(self) -> float:
        return self._end_value

    @end_value.setter
    def end_value(self, val: float) -> None:
        self._end_value = val

    def set_range(self, start: float, end: float):
        self._start_value = start
        self._end_value = end
        self.update()

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value
        self.update()

    @property
    def font(self) -> QFont:
        return self._font

    @font.setter
    def font(self, font: QFont) -> None:
        self._font = font

    @property
    def pen_width(self) -> int:
        return self._pen_width

    @pen_width.setter
    def pen_width(self, width: int) -> None:
        self._pen_width = width

    def initUI(self) -> None:
        self.setMinimumSize(200, 200)

    def getAdjustedRect(self) -> QRectF:
        leftMargin = (self._margin_percent.left * self._side) / 100
        rightmargin = (self._margin_percent.right * self._side) / 100
        topMargin = (self._margin_percent.top * self._side) / 100
        bottomMargin = (self._margin_percent.bottom * self._side) / 100
        adjustedRect = self._baseRect.adjusted(leftMargin, rightmargin,
                                               -topMargin, -bottomMargin)
        return adjustedRect

    def paintEvent(self, event: QPaintEvent) -> None:
        self._painter = QPainter()
        self._painter.begin(self)
        self._painter.setRenderHint(QPainter.TextAntialiasing, True)
        self._painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        self.drawWidget()
        self._painter.end()

    def drawWidget(self) -> None:
        size = self.size()
        self._side = SIDE_FRACTION * min(size.width(), size.height())
        self._baseRect = QRectF(0, 0, self._side, self._side)

        self.drawProgressBar()
        self.drawCenterText()

    def drawProgressBar(self) -> None:
        adjustedRect = self.getAdjustedRect()
        with DrawingPainter(self._painter, QPen(Qt.green, self._pen_width, Qt.SolidLine, Qt.FlatCap)) as painter:
            painter.drawEllipse(adjustedRect)

        with DrawingPainter(self._painter, QPen(Qt.red, self._pen_width, Qt.SolidLine, Qt.FlatCap)) as painter:
            startAngle = self.PositionTop * PYQT_ANGLE_PRECISION
            endAngle = -int(((self.value - self.start_value) /
                             (self.end_value - self.start_value)) * FULL_ANGLE * PYQT_ANGLE_PRECISION)
            painter.drawArc(adjustedRect, startAngle, endAngle)

    def drawCenterText(self) -> None:
        substitution = {'value': str(round(self.value, 2)), 'end_value': str(round(self.end_value, 2))} # type: Dict[str, str]
        text = self._str_template.substitute(substitution)
        self._painter.setFont(self.font)
        self._painter.drawText(self._baseRect, Qt.AlignCenter, text)
