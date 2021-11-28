# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from xitomatl.icon import task_icon
from xitomatl.pomodoro import Pomodoro, State

DEFAULT_ICON_SIZE = 64


def start_task_callback(pomodoro, index):
    def start_task():
        return pomodoro.start_task(index)

    return start_task


def in_menu_tasks(tasks):
    for index, task in enumerate(tasks):
        if task.in_menu:
            yield index, task


def add_task_actions(menu, pomodoro, icon_size):
    actions = {}
    for number, (index, task) in enumerate(in_menu_tasks(pomodoro.tasks)):
        text = f"&{number + 1}. {task}"
        start_task = start_task_callback(pomodoro, index)
        act = menu.addAction(text, start_task)
        icon = task_icon(task, State.Running, task.minutes, icon_size)
        act.setIcon(icon)
        actions[index] = act

    return actions


class App:
    def __init__(self, argv, settings):
        self.app = QApplication(argv)

        self.pomodoro = Pomodoro(settings)
        self.pomodoro.state_changed.connect(self.on_state_changed)

        self.icon = QSystemTrayIcon()
        self.icon.activated.connect(self.on_activated)

        self.icon_size = int(settings.value("icon_size", DEFAULT_ICON_SIZE))

        menu = QMenu()
        menu.addAction(
            QIcon.fromTheme("media-playback-start"),
            "&Start",
            self.pomodoro.start,
        )
        menu.addAction(
            QIcon.fromTheme("media-skip-forward"), "&Next", self.pomodoro.next
        )
        menu.addAction(
            QIcon.fromTheme("media-playback-stop"), "&Stop", self.pomodoro.stop
        )
        menu.addSeparator()
        self.task_actions = add_task_actions(
            menu, self.pomodoro, self.icon_size
        )
        menu.addSeparator()
        menu.addAction(
            QIcon.fromTheme("application-exit"), "&Quit", self.app.quit
        )
        self.icon.setContextMenu(menu)

        self.current_task_index = -1

        self.on_state_changed()
        self.icon.show()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.pomodoro.state == State.Running:
                self.pomodoro.next()
            else:
                self.pomodoro.start()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.pomodoro.stop()

    def on_state_changed(self):
        icon = task_icon(
            self.pomodoro.current_task(),
            self.pomodoro.state,
            self.pomodoro.remaining_minutes(),
            self.icon_size,
        )
        self.icon.setIcon(icon)
        self.icon.setToolTip(
            f"{QApplication.applicationName()}: {self.pomodoro}"
        )

        act = self.task_actions.get(self.current_task_index)
        if act:
            act.setText(act.text()[2:])

        self.current_task_index = self.pomodoro.current_task_index
        act = self.task_actions.get(self.current_task_index)
        if act:
            act.setText(f"▶ {act.text()}")

    def exec(self):
        return self.app.exec()
