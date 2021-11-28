# SPDX-License-Identifier: LGPL-2.0-or-later
from contextlib import contextmanager

from PySide6.QtCore import QElapsedTimer, QPoint, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPixmap

from xitomatl.log import log
from xitomatl.tasks import (
    DEFAULT_TASK_CACHE_KEY,
    Break,
    Task,
    read_task,
    read_tasks,
    to_bool,
)

ICON_SIZE = 64
SHORT_BREAK_COUNT = 3


def default_pomodoro_tasks():
    focus = Task(minutes=25)
    short_break = Break(minutes=5)
    long_break = Break(minutes=30, in_menu=True)
    return [focus, short_break] * SHORT_BREAK_COUNT + [focus, long_break]


def default_stopped_task():
    return Task(
        name="stopped",
        color=QColor("#ff0040"),
        text_color=QColor("white"),
    )


@contextmanager
def readArray(settings, name):
    try:
        settings.beginReadArray(name)
        yield
    except Exception:
        log.exception(
            "Failed to read [%s] from configuration file %s",
            name,
            settings.fileName(),
        )
        raise
    finally:
        settings.endArray()


@contextmanager
def enterGroup(settings, name):
    try:
        settings.beginGroup(name)
        yield
    except Exception:
        log.exception(
            "Failed to read [%s] from configuration file %s",
            name,
            settings.fileName(),
        )
        raise
    finally:
        settings.endGroup()


class State:
    Stopped = 0
    Running = 1


class Pomodoro:
    def __init__(self, settings):
        self.state = State.Stopped

        with readArray(settings, "tasks"):
            self.tasks = read_tasks(settings) or default_pomodoro_tasks()

        with enterGroup(settings, "stopped"):
            task_cache = {DEFAULT_TASK_CACHE_KEY: default_stopped_task()}
            self.stopped_task = read_task(settings, task_cache)

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
            painter.setPen(Qt.NoPen)

            task = self.current_task()

            color = task.color
            text_color = task.text_color
            if self.state == State.Running:
                remaining = self.remaining_minutes()
                if remaining <= 0:
                    remaining = -remaining
                    color = task.important_color
                    text_color = task.important_text_color

            pad = task.icon_padding * self.icon_size // 100
            painter.setBrush(color)
            rect = pix.rect().adjusted(pad, pad, -pad, -pad)
            painter.drawRoundedRect(
                rect, task.icon_radius, task.icon_radius, Qt.RelativeSize
            )

            if self.state == State.Stopped:
                painter.setBrush(text_color)
                pad *= 3
                rect = pix.rect().adjusted(pad, pad, -pad, -pad)
                painter.drawRect(rect)
            elif self.state == State.Running:
                icon_text = str(remaining)

                font = QFont(task.font)
                font.setPixelSize(task.text_size * self.icon_size // 100)

                painter.setFont(font)
                painter.setPen(text_color)

                metrics = QFontMetrics(font)
                rect = metrics.tightBoundingRect(icon_text)
                bottom_left = rect.bottomLeft()
                x = (
                    (width - rect.width()) / 2
                    + task.text_x * width / 100
                    - bottom_left.x()
                )
                y = (
                    (height - rect.height()) / 2
                    + task.text_y * height / 100
                    - bottom_left.y()
                )
                pos = QPoint(x, height - y)
                painter.drawText(pos, icon_text)
        finally:
            painter.end()

        return QIcon(pix)

    def current_task(self):
        if self.state == State.Running:
            return self.tasks[self.current_task_index]

        return self.stopped_task

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

        interval = remaining % 60000
        if interval == 0:
            interval += 60000
        interval += 1000
        log.debug("Scheduling next update in %s ms", interval)
        self.timer.start(interval)
