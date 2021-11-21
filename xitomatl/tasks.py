# SPDX-License-Identifier: LGPL-2.0-or-later
from copy import copy

DEFAULT_ICON_FONT = "Overpass ExtraBold"


class Task:
    def __init__(
        self,
        name="focus",
        minutes=25,
        color="#007ba7",
        text_color="white",
        important_color="#ff0040",
        font=DEFAULT_ICON_FONT,
        in_menu=True,
    ):
        self.minutes = minutes
        self.name = name
        self.color = color
        self.text_color = text_color
        self.important_color = important_color
        self.font = font
        self.in_menu = in_menu

    def __str__(self):
        return f"{self.name}/{self.minutes}"


class Break(Task):
    def __init__(self, minutes=5, in_menu=False):
        super().__init__(
            name="break",
            minutes=minutes,
            color="#de3163",
            text_color="white",
            important_color="white",
            in_menu=in_menu,
        )


FOCUS = Task(minutes=25)
SHORT = Break(minutes=5)
LONG = Break(minutes=30, in_menu=True)
SHORT_BREAK_COUNT = 4
DEFAULT_TASKS = [FOCUS, SHORT] * SHORT_BREAK_COUNT + [FOCUS, LONG]


def read_task(index, settings, task_cache):
    settings.setArrayIndex(index)
    name = settings.value("name", "focus")
    task = task_cache.setdefault(name, Task(name))
    KEYS = [
        "minutes",
        "color",
        "text_color",
        "important_color",
        "font",
        "in_menu",
    ]
    for k in KEYS:
        v = settings.value(k)
        if v:
            setattr(task, k, v)
    task.minutes = int(task.minutes)
    task.in_menu = str(task.in_menu).lower() in ("true", "1", "yes", "on")
    return copy(task)


def read_tasks(settings):
    try:
        task_count = settings.beginReadArray("tasks")
        if task_count == 0:
            return []
        task_cache = {task.name: task for task in (Task(), Break())}
        return [
            read_task(index, settings, task_cache)
            for index in range(task_count)
        ]
    finally:
        settings.endArray()
