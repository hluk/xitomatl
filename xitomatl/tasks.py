# SPDX-License-Identifier: LGPL-2.0-or-later
from copy import copy
from dataclasses import dataclass, field, fields

from PySide6.QtGui import QColor

DEFAULT_FONT = "Noto Sans Mono; SemiBold"
DEFAULT_TIMEOUT_FONT = "Noto Sans Mono; Bold"
DEFAULT_TASK_CACHE_KEY = "__default__"


def to_bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


class TimedOutTask:
    """
    Wrapper for task providing timeout_* attributes instead of normal ones.
    """

    def __init__(self, task):
        self.task = task

    def __getattr__(self, attr):
        if hasattr(self.task, "timeout_" + attr):
            return getattr(self.task, "timeout_" + attr)
        return getattr(self.task, attr)


def color_field(color_name):
    # pylint: disable=invalid-field-call
    return field(default_factory=lambda: QColor(color_name))


@dataclass
class Task:
    name: str = "focus"
    minutes: int = 25
    in_menu: bool = True
    command_start: str = ""
    command_stop: str = ""
    command_finish: str = ""
    image: str = ""

    # Normal appearance options
    font: str = DEFAULT_FONT
    color: QColor = color_field("#007ba7")
    line_color: QColor = color_field("transparent")
    line_width: int = 0
    text_color: QColor = color_field("white")
    text_stroke_width: int = 0
    text_stroke_color: QColor = color_field("transparent")
    text_size: int = 65
    text_x: int = 0
    text_y: int = 0
    icon_radius: int = 30
    icon_padding: int = 10

    # Timed out appearance options
    timeout_font = DEFAULT_TIMEOUT_FONT
    timeout_color: QColor = color_field("#ff0040")
    timeout_line_color: QColor = color_field("transparent")
    timeout_line_width: int = 0
    timeout_text_color: QColor = color_field("white")
    timeout_text_stroke_width: int = 0
    timeout_text_stroke_color: QColor = color_field("transparent")
    timeout_text_size: int = 65
    timeout_text_x: int = 0
    timeout_text_y: int = 0
    timeout_icon_radius: int = 30
    timeout_icon_padding: int = 10

    animated: bool = True

    def __str__(self):
        return f"{self.name}/{self.minutes}"

    def as_timed_out(self):
        return TimedOutTask(self)


class Break(Task):
    def __init__(self, minutes=5, in_menu=False):
        super().__init__(
            name="break",
            minutes=minutes,
            color=QColor("#de3163"),
            text_color=QColor("white"),
            timeout_color=QColor("#ffbf00"),
            timeout_text_color=QColor("black"),
            in_menu=in_menu,
            icon_radius=100,
            text_y=0,
            animated=True,
        )


def read_task(settings, task_cache):
    name = settings.value("name", "focus")
    default_task = task_cache[DEFAULT_TASK_CACHE_KEY]
    default_task.name = name
    task = task_cache.setdefault(name, default_task)

    for field_ in fields(Task):
        value = settings.value(field_.name)
        if value:
            convert = field_.type
            if convert is bool:
                convert = to_bool
            setattr(task, field_.name, convert(value))

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
