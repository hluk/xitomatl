# SPDX-License-Identifier: LGPL-2.0-or-later
from copy import copy

from PySide6.QtGui import QColor

DEFAULT_ICON_FONT = "Noto Sans Mono Condensed ExtraBold"
DEFAULT_TASK_CACHE_KEY = "__default__"
DEFAULT_TASK_ARGS = dict(
    name="focus",
    minutes=25,
    color=QColor("#007ba7"),
    line_color=QColor("transparent"),
    line_width=0,
    text_color=QColor("white"),
    important_color=QColor("#ff0040"),
    important_text_color=QColor("white"),
    important_line_color=QColor("transparent"),
    font=DEFAULT_ICON_FONT,
    in_menu=True,
    text_size=65,
    text_x=0,
    text_y=0,
    icon_radius=30,
    icon_padding=10,
    command_start="",
    command_stop="",
    command_finish="",
)


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


class Task:
    def __init__(self, **kwargs):
        for k, v in DEFAULT_TASK_ARGS.items():
            setattr(self, k, kwargs.get(k, v))

    def __str__(self):
        return f"{self.name}/{self.minutes}"


class Break(Task):
    def __init__(self, minutes=5, in_menu=False):
        super().__init__(
            name="break",
            minutes=minutes,
            color=QColor("#de3163"),
            text_color=QColor("white"),
            important_color=QColor("#ffbf00"),
            important_text_color=QColor("black"),
            in_menu=in_menu,
            icon_radius=100,
            text_y=0,
        )


def read_task(settings, task_cache):
    name = settings.value("name", "focus")
    default_task = task_cache[DEFAULT_TASK_CACHE_KEY]
    default_task.name = name
    task = task_cache.setdefault(name, default_task)

    for key, default_value in DEFAULT_TASK_ARGS.items():
        value = settings.value(key)
        if value:
            convert = type(default_value)
            if convert is bool:
                convert = to_bool
            setattr(task, key, convert(value))

    task_cache[DEFAULT_TASK_CACHE_KEY] = copy(task)
    return copy(task)


def read_tasks(settings):
    task_cache = {task.name: task for task in (Task(), Break())}
    task_cache[DEFAULT_TASK_CACHE_KEY] = Task()
    tasks = []

    settings.setArrayIndex(0)
    while settings.childKeys():
        tasks.append(read_task(settings, task_cache))
        settings.setArrayIndex(len(tasks))

    return tasks
