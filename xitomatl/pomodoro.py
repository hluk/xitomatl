# SPDX-License-Identifier: LGPL-2.0-or-later
import shlex
from contextlib import contextmanager
from subprocess import run  # nosec B404

from PySide6.QtCore import QElapsedTimer, Qt, QTimer
from PySide6.QtGui import QColor

from xitomatl.log import log
from xitomatl.state import State
from xitomatl.tasks import (
    DEFAULT_TASK_CACHE_KEY,
    Break,
    Task,
    read_task,
    read_tasks,
    to_bool,
)

SHORT_BREAK_COUNT = 3


def _run(command):
    for subcommand in command.split("\n"):
        subcommand = subcommand.strip()
        if subcommand:
            log.info("Executing: %s", subcommand)
            args = shlex.split(subcommand)
            run(args, shell=False, check=True)  # nosec B603


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

    def current_task(self):
        if self.state == State.Running:
            return self.tasks[self.current_task_index]

        return self.stopped_task

    def start_task(self, index):
        log.info("[%s] Select start", self)
        if self.state == State.Running:
            self._run_command_stop()
        self.state = State.Running
        self.current_task_index = index
        self.on_changed()
        self._run_command_start()

    def stop(self):
        log.info("[%s] Stop", self)
        if self.state == State.Running:
            self._run_command_stop()
        self.state = State.Stopped
        self.current_task_index = 0
        self.on_changed()

    def elapsed_minutes(self):
        return int(self.elapsed.elapsed() / 60000)

    def remaining_minutes(self):
        return self.current_task().minutes - self.elapsed_minutes()

    def start(self):
        log.info("[%s] Start", self)
        if self.state == State.Running:
            self._run_command_stop()
        self.state = State.Running
        self.on_changed()
        self._run_command_start()

    def next(self):
        log.info("[%s] Next", self)
        if self.state == State.Running:
            self._run_command_stop()
        self.current_task_index = (self.current_task_index + 1) % len(
            self.tasks
        )
        self.on_changed()
        self._run_command_start()

    def finish(self):
        log.info("[%s] Finished", self)
        self.finished = True
        self._run_command_finish()

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

    def _run_command_start(self):
        task = self.current_task()
        _run(task.command_start)

    def _run_command_stop(self):
        task = self.current_task()
        _run(task.command_stop)

    def _run_command_finish(self):
        task = self.current_task()
        _run(task.command_finish)
