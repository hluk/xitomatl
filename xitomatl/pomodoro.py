# SPDX-License-Identifier: LGPL-2.0-or-later
import os

from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap

from xitomatl.log import log
from xitomatl.tasks import Break, Task, read_tasks, to_bool

DIR = os.path.abspath(os.path.dirname(__file__))
ICON_SIZE = 32


def default_pomodoro_tasks():
    focus = Task(minutes=25)
    short_break = Break(minutes=5)
    long_break = Break(minutes=30, in_menu=True)
    short_break_count = 3
    return [focus, short_break] * short_break_count + [focus, long_break]


class State:
    Stopped = 0
    Running = 1


class Pomodoro:
    def __init__(self, settings):
        self.state = State.Stopped

        try:
            self.tasks = read_tasks(settings) or default_pomodoro_tasks()
        except Exception:
            log.exception(
                "Failed to read [tasks] from configuration file %s",
                settings.fileName(),
            )
            raise

        self.current_task_index = 0
        self.elapsed = QElapsedTimer()
        self.elapsed.start()

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setTimerType(Qt.VeryCoarseTimer)
        self.timer.timeout.connect(self.on_timeout)
        self.finished = True

        self.icon_size = int(settings.value("icon_size", ICON_SIZE))

        log.info("[%s] Initialized", self)

        autostart = settings.value("autostart", "true")
        if to_bool(autostart):
            self.start()

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

            task = self.current_task()

            pad = int(task.icon_padding * self.icon_size / 100)
            painter.setBrush(task.color)
            rect = pix.rect().adjusted(pad, pad, -pad, -pad)
            painter.drawRoundedRect(
                rect, task.icon_radius, task.icon_radius, Qt.RelativeSize
            )

            if self.state == State.Stopped:
                painter.setBrush(task.important_color)
                pad *= 3
                rect = pix.rect().adjusted(pad, pad, -pad, -pad)
                painter.drawEllipse(rect)
            elif self.state == State.Running:
                remaining = self.remaining_minutes()
                if remaining > 0:
                    text_color = task.text_color
                else:
                    remaining = -remaining
                    text_color = task.important_color

                icon_text = str(remaining)

                font = QFont(task.font)
                font.setPixelSize(task.text_size * self.icon_size / 100)

                painter.setFont(font)
                painter.setPen(text_color)

                dx = int(task.text_x * self.icon_size / 100)
                dy = int(task.text_y * self.icon_size / 100)
                rect = pix.rect().adjusted(dx, dy, dx, dy)
                painter.drawText(rect, Qt.AlignCenter, icon_text)
        finally:
            painter.end()

        return QIcon(pix)

    def current_task(self):
        return self.tasks[self.current_task_index]

    def start_task(self, index):
        log.info("[%s] Select start", self)
        self.state = State.Running
        self.current_task_index = index
        self.on_changed()

    def stop(self):
        log.info("[%s] Stop", self)
        self.state = State.Stopped
        self.current_task_index = 0
        self.on_changed()

    def elapsed_minutes(self):
        return int(self.elapsed.elapsed() / 60000)

    def remaining_minutes(self):
        return self.current_task().minutes - self.elapsed_minutes()

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
        self.finished = True

    @property
    def state_changed(self):
        return self.timer.timeout

    def on_changed(self):
        self.elapsed.restart()
        self.finished = False
        log.info("[%s]", self)
        self.timer.timeout.emit()

    def on_timeout(self):
        if self.state == State.Stopped:
            return

        elapsed = self.elapsed.elapsed()
        remaining = self.current_task().minutes * 60000 - elapsed

        if not self.finished and remaining <= 0:
            self.finish()

        interval = remaining % 60000 + 1000
        self.timer.start(interval)
