# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from xitomatl.pomodoro import Pomodoro, State


def start_task_callback(pomodoro, index):
    def start_task():
        return pomodoro.start_task(index)

    return start_task


class App:
    def __init__(self, argv, settings):
        self.app = QApplication(argv)

        self.pomodoro = Pomodoro(settings)
        self.pomodoro.state_changed.connect(self.on_state_changed)

        self.icon = QSystemTrayIcon()
        self.icon.activated.connect(self.on_activated)
        self.icon.setContextMenu(QMenu())

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
        self.icon.setToolTip(f"Pomodoro: {self.pomodoro}")

        menu = self.icon.contextMenu()
        menu.clear()
        menu.addAction("&Start", self.pomodoro.start)
        menu.addAction("&Next", self.pomodoro.next)
        menu.addAction("&Stop", self.pomodoro.stop)

        menu.addSeparator()
        number = 0
        for index, task in enumerate(self.pomodoro.tasks):
            if task.in_menu:
                number += 1
                text = f"&{number}. {task}"
                if index == self.pomodoro.current_task_index:
                    text = f">{text}"
                start_task = start_task_callback(self.pomodoro, index)
                menu.addAction(text, start_task)

        menu.addSeparator()
        menu.addAction("&Quit", self.app.quit)

    def exec(self):
        return self.app.exec()
