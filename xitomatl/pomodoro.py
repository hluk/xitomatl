# SPDX-License-Identifier: LGPL-2.0-or-later
from contextlib import contextmanager

from PySide6.QtCore import QElapsedTimer, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickView

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

DEFAULT_ICON_QML = """
import QtQuick 2.0
Item {
  width: icon_size
  height: icon_size
  Rectangle {
    color: icon_color
    width: parent.width - icon_padding * 2
    height: parent.height - icon_padding * 2
    radius: icon_radius
    anchors.centerIn: parent

    Text {
      visible: task_running
      color: text_color
      text: icon_text
      font.family: icon_font
      font.pixelSize: icon_font_size
      anchors.fill: parent
      horizontalAlignment: Text.AlignHCenter
      verticalAlignment: Text.AlignVCenter
    }

    Rectangle {
      visible: !task_running
      width: parent.width - icon_padding * 3
      height: parent.height - icon_padding * 3
      color: text_color
      anchors.centerIn: parent
    }
  }
}
"""


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

        self.quick_view = QQuickView()
        self.quick_view.setProperty("color", "transparent")
        self.quick_view.resize(self.icon_size, self.icon_size)
        context = self.quick_view.rootContext()
        context.setContextProperty("icon_size", self.icon_size)
        self._update()

        icon_qml = settings.value("icon_qml", DEFAULT_ICON_QML).encode("utf-8")
        component = QQmlComponent(self.quick_view.engine())
        component.setData(icon_qml, QUrl())
        self.quick_item = component.create(context)
        if not self.quick_item:
            raise RuntimeError(component.errorString())

        self.quick_view.setContent(QUrl(), component, self.quick_item)

    def __str__(self):
        state = "⏸︎" if self.state == State.Stopped else "⏵︎"
        return (
            f"{self.current_task_index + 1}/{len(self.tasks)}"
            f" {self.current_task()}"
            f" {self.elapsed_minutes()}m {state}"
        )

    def _update(self):
        task = self.current_task()

        color = task.color
        text_color = task.text_color
        remaining = ""
        if self.state == State.Running:
            remaining = self.remaining_minutes()
            if remaining <= 0:
                remaining = -remaining
                color = task.important_color
                text_color = task.important_text_color

        context = self.quick_view.rootContext()
        context.setContextProperty("task_name", task.name)
        context.setContextProperty("icon_font", task.font)
        context.setContextProperty("icon_color", color)
        context.setContextProperty("text_color", text_color)
        context.setContextProperty("icon_text", remaining)
        context.setContextProperty(
            "icon_font_size", task.text_size * self.icon_size // 100
        )
        context.setContextProperty(
            "text_x", task.text_x * self.icon_size // 100
        )
        context.setContextProperty(
            "text_y", task.text_y * self.icon_size // 100
        )
        context.setContextProperty(
            "icon_radius", task.icon_radius * self.icon_size // 200
        )
        context.setContextProperty(
            "icon_padding", task.icon_padding * self.icon_size // 100
        )
        context.setContextProperty("task_running", self.state == State.Running)

    def current_icon(self):
        self._update()
        image = self.quick_view.grabWindow().copy(
            0, 0, self.icon_size, self.icon_size
        )
        pix = QPixmap.fromImage(image)
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

        interval = remaining % 60000 + 1000
        self.timer.start(interval)
