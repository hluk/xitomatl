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

        self.menu = QMenu()
        self.menu.addAction("&Start", self.pomodoro.start)
        self.menu.addAction("&Next", self.pomodoro.next)
        self.menu.addAction("&Stop", self.pomodoro.stop)

        self.menu.addSeparator()
        menu_index = 1
        for index, task in enumerate(self.pomodoro.tasks):
            if task.in_menu:
                menu_index += 1
                start_task = start_task_callback(self.pomodoro, index)
                self.menu.addAction(f"&{menu_index}. {task}", start_task)

        self.menu.addSeparator()
        self.menu.addAction("&Quit", self.app.quit)

        self.icon.setContextMenu(self.menu)

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

        index = self.pomodoro.current_task_index + 1
        prefix = f"&{index}."
        for act in self.menu.actions():
            text = act.text()
            if text.startswith(prefix):
                act.setText(">" + text)
            elif text.startswith(">") and not text[1:].startswith(prefix):
                act.setText(text[1:])

    def exec(self):
        return self.app.exec()
