#!/usr/bin/env python3
import os
import sys

from PySide6.QtCore import QSettings
from PySide6.QtGui import QGuiApplication

from xitomatl.icon import task_icon
from xitomatl.log import init_logging, log
from xitomatl.pomodoro import Pomodoro
from xitomatl.state import State

ICON_SIZE = 48
DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(DIR, "images")


def main():
    app = QGuiApplication(sys.argv)  # noqa: F841
    init_logging()
    pomodoro = Pomodoro(QSettings())
    pomodoro.stop()
    stopped = pomodoro.current_task()
    task25 = pomodoro.tasks[0]
    break5 = pomodoro.tasks[1]
    break30 = pomodoro.tasks[-1]
    images = (
        (stopped, State.Stopped, 0),
        (task25, State.Running, 25),
        (task25, State.Running, 1),
        (task25, State.Running, 0),
        (task25, State.Running, -1),
        (break5, State.Running, 5),
        (break5, State.Running, 1),
        (break5, State.Running, 0),
        (break5, State.Running, -1),
        (break30, State.Running, 30),
    )
    for task, state, minutes in images:
        if state == State.Running:
            filename = f"{task.name}{minutes}.png"
        else:
            filename = "stopped.png"

        path = os.path.join(IMAGE_DIR, filename)
        log.info("Saving %s", path)

        icon = task_icon(task, state, minutes, ICON_SIZE)
        pix = icon.pixmap(ICON_SIZE)
        pix.save(path)


if __name__ == "__main__":
    main()
