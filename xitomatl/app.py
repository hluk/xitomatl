# SPDX-License-Identifier: LGPL-2.0-or-later
from bisect import bisect_left
from functools import partial

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from xitomatl.animation import NotifyAnimation
from xitomatl.icon import task_icon
from xitomatl.pomodoro import Pomodoro, State

DEFAULT_ICON_SIZE = 64
DEFAULT_DOUBLE_CLICK_INTERVAL_MS = 100
PROPERTY_INDEX = "xitomatl_task_index"


def add_task_actions(menu, pomodoro, icon_size):
    actions = {}
    for index, task in ((i, t) for i, t in enumerate(pomodoro.tasks) if t.in_menu):
        text = f"&{index + 1}. {task}"
        act = menu.addAction(text, partial(pomodoro.start_task, index))
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

        self.animation = NotifyAnimation()
        self.animation.icon_changed.connect(self.icon.setIcon)

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
        self.task_actions = add_task_actions(menu, self.pomodoro, self.icon_size)
        self.task_index_list = list(self.task_actions.keys())
        menu.addSeparator()
        menu.addAction(QIcon.fromTheme("application-exit"), "&Quit", self.app.quit)
        self.icon.setContextMenu(menu)

        self.current_task_index = -2
        self.current_action = None

        self.on_state_changed()
        self.icon.show()

        # Workaround for interpreting double clicks on tray icon as three
        # single clicks in waybar.
        self.click_timer = QTimer()
        double_click_interval_ms = int(
            settings.value("double_click_interval_ms", DEFAULT_DOUBLE_CLICK_INTERVAL_MS)
        )
        self.click_timer.setSingleShot(True)
        self.click_timer.setInterval(double_click_interval_ms)
        self.click_timer.timeout.connect(self.on_icon_single_click)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.click_timer.start()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            self.on_icon_middle_click()

    def on_icon_single_click(self):
        if self.pomodoro.state == State.Running:
            self.pomodoro.next()
        else:
            self.pomodoro.start()

    def on_icon_middle_click(self):
        self.pomodoro.stop()

    def on_state_changed(self):
        task = self.pomodoro.current_task()
        remaining = self.pomodoro.remaining_minutes()
        icon = task_icon(
            task,
            self.pomodoro.state,
            remaining,
            self.icon_size,
        )

        self.animation.set_icon(icon)
        if task.animated and remaining <= 0:
            self.animation.start()
        else:
            self.animation.stop()

        self.icon.setToolTip(f"{QApplication.applicationName()}: {self.pomodoro}")

        if self.current_task_index != self.pomodoro.current_task_index:
            if self.current_action:
                self.current_action.setText(
                    self.current_action.text().split(maxsplit=1)[-1]
                )

            self.current_task_index = self.pomodoro.current_task_index
            i = bisect_left(
                self.task_index_list,
                self.current_task_index,
            )
            i = self.task_index_list[i % len(self.pomodoro.tasks)]
            act = self.task_actions[i]
            if i == self.current_task_index:
                act.setText(f"▶ {act.text()}")
            else:
                act.setText(f"⏸ {act.text()}")
            self.current_action = act

            self.animation.once()

    def exec(self):
        return self.app.exec()
