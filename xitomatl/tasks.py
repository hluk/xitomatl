# SPDX-License-Identifier: LGPL-2.0-or-later
from copy import copy

from PySide6.QtGui import QColor

DEFAULT_ICON_FONT = "Overpass ExtraBold"
DEFAULT_TASK_CACHE_KEY = "__default__"


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


class Task:
    def __init__(
        self,
        name="focus",
        minutes=25,
        color=QColor("#007ba7"),
        text_color=QColor("white"),
        important_color=QColor("#ff0040"),
        font=DEFAULT_ICON_FONT,
        in_menu=True,
        text_size=65,
        text_x=0,
        text_y=15,
        icon_radius=30,
        icon_padding=10,
    ):
        self.minutes = minutes
        self.name = name
        self.color = color
        self.text_color = text_color
        self.important_color = important_color
        self.font = font
        self.in_menu = in_menu
        self.text_size = text_size
        self.text_x = text_x
        self.text_y = text_y
        self.icon_radius = icon_radius
        self.icon_padding = icon_padding

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
            in_menu=in_menu,
            icon_radius=100,
            text_y=0,
        )


def read_task(settings, task_cache):
    name = settings.value("name", "focus")
    default_task = task_cache[DEFAULT_TASK_CACHE_KEY]
    default_task.name = name
    task = task_cache.setdefault(name, default_task)

    KEYS = (
        ("minutes", int),
        ("color", QColor),
        ("text_color", QColor),
        ("important_color", QColor),
        ("font", str),
        ("in_menu", to_bool),
        ("text_size", int),
        ("text_x", int),
        ("text_y", int),
        ("icon_radius", int),
        ("icon_padding", int),
    )
    for key, convert in KEYS:
        value = settings.value(key)
        if value:
            setattr(task, key, convert(value))

    task_cache[DEFAULT_TASK_CACHE_KEY] = copy(task)
    return copy(task)


def read_tasks(settings):
    try:
        task_cache = {task.name: task for task in (Task(), Break())}
        task_cache[DEFAULT_TASK_CACHE_KEY] = Task()
        tasks = []

        settings.beginReadArray("tasks")
        settings.setArrayIndex(0)
        while settings.childKeys():
            tasks.append(read_task(settings, task_cache))
            settings.setArrayIndex(len(tasks))

        return tasks
    finally:
        settings.endArray()
