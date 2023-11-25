# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtCore import (
    QEasingCurve,
    QObject,
    Qt,
    QTimer,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPixmap,
    QTransform,
)


class NotifyAnimation(QObject):
    icon_changed = Signal(QIcon)

    def __init__(self):
        super().__init__()
        self.rotation = 0.0
        self.running = False
        self.fps = 24

        self.curve_flash = QEasingCurve(QEasingCurve.Type.InOutExpo)
        self.flash_color = QColor(255, 255, 100)

        self.curve1 = QEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim1 = QVariantAnimation()
        self.anim1.setEasingCurve(self.curve1)
        self.anim1.setStartValue(self.rotation)
        self.anim1.setEndValue(-15.0)
        self.anim1.setDuration(250)
        self.anim1.valueChanged.connect(self.set_rotation)

        self.curve2 = QEasingCurve(QEasingCurve.Type.OutElastic)
        self.curve2.setAmplitude(3)
        self.curve2.setPeriod(0.2)
        self.anim2 = QVariantAnimation()
        self.anim2.setEasingCurve(self.curve2)
        self.anim2.setStartValue(self.anim1.endValue())
        self.anim2.setEndValue(self.rotation)
        self.anim2.setDuration(1500)
        self.anim2.valueChanged.connect(self.set_rotation)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(20000)

        self.anim1.finished.connect(self.anim2.start)
        self.anim2.finished.connect(self.timer.start)
        self.timer.timeout.connect(self._loop)

        self.icon = QPixmap()

    @property
    def interval(self):
        return self.timer.interval()

    @interval.setter
    def interval(self, milliseconds):
        self.timer.setInterval(milliseconds)

    def start(self):
        self.running = True
        self.once()

    def stop(self):
        self.running = False

    def once(self):
        self.timer.stop()
        self.anim2.stop()
        self.anim1.setStartValue(self.rotation)
        self.anim1.start()

    def set_icon(self, icon):
        self.icon = icon
        self.update_icon()

    def set_rotation(self, value):
        self.rotation = value
        self.update_icon()

    def update_icon(self):
        transform = QTransform()
        transform.rotate(self.rotation)
        icon = self.icon.transformed(
            transform, Qt.TransformationMode.SmoothTransformation
        )
        self._flash(icon)
        self.icon_changed.emit(QIcon(icon))

    def _flash(self, icon):
        time = self.anim1.currentTime() + self.anim2.currentTime()
        duration = self.anim1.duration() + self.anim2.duration()

        progress = time / duration
        value = self.curve_flash.valueForProgress(progress)
        alpha = 2.0 * value
        if alpha > 1.0:
            alpha = 2.0 - alpha
        self.flash_color.setAlphaF(alpha)

        area = icon.rect()
        scale = 1.2
        gradient = QLinearGradient(area.topRight() * scale, area.bottomLeft() * scale)
        gradient.setColorAt(0.0, Qt.GlobalColor.transparent)
        gradient.setColorAt(value, self.flash_color)
        gradient.setColorAt(1.0, Qt.GlobalColor.transparent)

        painter = QPainter(icon)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
        painter.fillRect(area, gradient)
        painter.end()

    def _loop(self):
        if self.running:
            self.once()
