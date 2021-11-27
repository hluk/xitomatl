# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from xitomatl.pomodoro import Pomodoro, State


def color_icon(color_name):
    pix = QPixmap(1, 1)
    pix.fill(QColor(color_name))
    return QIcon(pix)


def start_task_callback(pomodoro, index):
    def start_task():
        return pomodoro.start_task(index)

    return start_task


def in_menu_tasks(tasks):
    for index, task in enumerate(tasks):
        if task.in_menu:
            yield index, task


def add_task_actions(menu, pomodoro):
    actions = {}
    for number, (index, task) in enumerate(in_menu_tasks(pomodoro.tasks)):
        text = f"&{number + 1}. {task}"
        start_task = start_task_callback(pomodoro, index)
        act = menu.addAction(text, start_task)
        act.setIcon(color_icon(task.color))
        actions[index] = act

    return actions


class App:
    def __init__(self, argv, settings):
        self.app = QApplication(argv)

        self.pomodoro = Pomodoro(settings)
        self.pomodoro.state_changed.connect(self.on_state_changed)

        self.icon = QSystemTrayIcon()
        self.icon.activated.connect(self.on_activated)

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
        self.task_actions = add_task_actions(menu, self.pomodoro)
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
        self.icon.setIcon(self.pomodoro.current_icon())
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
