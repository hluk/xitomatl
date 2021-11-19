# SPDX-License-Identifier: LGPL-2.0-or-later
import os

from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap

from xitomatl.log import log

DIR = os.path.abspath(os.path.dirname(__file__))
ICON_SIZE = 32
ICON_TEXT_SIZE = 65
ICON_TEXT_X = 0
ICON_TEXT_Y = 15
ICON_RADIUS = 30
ICON_PADDING = 10
ICON_FONT = "Overpass ExtraBold"


class Task:
    def __init__(self, minutes, name=None):
        self.minutes = minutes

    def __str__(self):
        return f"{self.name}/{self.minutes}"


class Focus(Task):
    name = "focus"
    color = "#007ba7"
    text_color = "white"
    important_color = "#ff0040"


class Break(Task):
    name = "break"
    color = "#de3163"
    text_color = "white"
    important_color = "white"


FOCUS = Focus(minutes=25)
SHORT = Break(minutes=5)
LONG = Break(minutes=30)
SHORT_COUNT = 4


class State:
    Stopped = 0
    Running = 1


class Pomodoro:
    def __init__(self, settings):
        self.state = State.Stopped

        self.tasks = [FOCUS, SHORT] * SHORT_COUNT + [FOCUS, LONG]
        self.current_task_index = 0
        self.elapsed = QElapsedTimer()
        self.elapsed.start()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setTimerType(Qt.VeryCoarseTimer)
        self.timer.timeout.connect(self.on_timeout)

        self.font_name = settings.value("font_name", ICON_FONT)
        self.icon_size = int(settings.value("icon_size", ICON_SIZE))
        self.icon_text_size = int(
            settings.value("icon_text_size", ICON_TEXT_SIZE)
        )
        self.icon_radius = int(settings.value("icon_radius", ICON_RADIUS))
        self.icon_padding = int(settings.value("icon_padding", ICON_PADDING))
        self.icon_text_x = int(settings.value("icon_text_x", ICON_TEXT_X))
        self.icon_text_y = int(settings.value("icon_text_y", ICON_TEXT_Y))

        log.info("[%s] Initialized", self)

    def __str__(self):
        state = "⏸︎" if self.state == State.Stopped else "⏵︎"
        return (
            f"{self.current_task_index + 1}/{len(self.tasks)}"
            f" {self.current_task()}"
            f" {self.elapsed_minutes()}m {state}"
        )

    def current_icon(self):
        width = self.icon_size
        height = self.icon_size
        pix = QPixmap(width, height)
        pix.fill(Qt.transparent)
        try:
            painter = QPainter(pix)
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(Qt.transparent)
            pen.setWidth(0)
            painter.setPen(pen)

            pad = int(self.icon_padding * self.icon_size / 100)
            task = self.current_task()
            color = QColor(task.color)
            painter.setBrush(color)
            rect = pix.rect().adjusted(pad, pad, -pad, -pad)
            painter.drawRoundedRect(
                rect, self.icon_radius, self.icon_radius, Qt.RelativeSize
            )

            if self.state == State.Stopped:
                color = QColor(task.important_color)
                painter.setBrush(color)
                pad *= 3
                rect = pix.rect().adjusted(pad, pad, -pad, -pad)
                painter.drawEllipse(rect)

            if self.state == State.Running:
                icon_text = str(self.remaining_minutes())

                font = QFont(self.font_name)
                font.setPixelSize(self.icon_text_size * self.icon_size / 100)

                painter.setFont(font)
                painter.setPen(task.text_color)

                dx = int(self.icon_text_x * self.icon_size / 100)
                dy = int(self.icon_text_y * self.icon_size / 100)
                rect = pix.rect().adjusted(dx, dy, dx, dy)
                painter.drawText(rect, Qt.AlignCenter, icon_text)
        finally:
            painter.end()

        return QIcon(pix)

    def current_task(self):
        return self.tasks[self.current_task_index]

    def stop(self):
        log.info("[%s] Stop", self)
        self.state = State.Stopped
        self.current_task_index = 0
        self.on_changed()

    def elapsed_minutes(self):
        return int(self.elapsed.elapsed() / 60000)

    def remaining_minutes(self):
        remaining = self.current_task().minutes - self.elapsed_minutes()
        if remaining < 0:
            return 0
        return remaining

    def start(self):
        log.info("[%s] Start", self)
        self.state = State.Running
        self.on_changed()

    def next(self):
        log.info("[%s] Next", self)
        self.current_task_index = (self.current_task_index + 1) % len(
            self.tasks
        )
        self.on_changed()

    def finish(self):
        log.info("[%s] Finished", self)
        self.current_task_index = (self.current_task_index + 1) % len(
            self.tasks
        )
        self.state = State.Stopped
        self.on_changed()

    @property
    def state_changed(self):
        return self.timer.timeout

    def on_changed(self):
        self.elapsed.restart()
        log.info("[%s]", self)
        self.timer.timeout.emit()

    def on_timeout(self):
        if self.state == State.Running:
            elapsed = self.elapsed.elapsed()
            remaining = self.current_task().minutes * 60000 - elapsed
            if remaining > 0:
                interval = remaining % 60000 + 1000
                self.timer.start(interval)
            else:
                self.finish()
