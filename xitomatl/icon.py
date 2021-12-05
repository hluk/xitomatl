# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QFont, QFontMetrics, QIcon, QPainter, QPen, QPixmap

from xitomatl.state import State


def task_icon(task, state, remaining_minutes, icon_size):
    """Created QIcon for given task and state."""
    width = icon_size
    height = icon_size
    pix = QPixmap(width, height)
    pix.fill(Qt.transparent)
    try:
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        color = task.color
        text_color = task.text_color
        line_color = task.line_color
        if state == State.Running:
            remaining = remaining_minutes
            if remaining <= 0:
                remaining = -remaining
                color = task.important_color
                text_color = task.important_text_color
                line_color = task.important_line_color

        painter.setPen(QPen(line_color, task.line_width * icon_size // 100))

        pad = task.icon_padding * icon_size // 100
        painter.setBrush(color)
        rect = pix.rect().adjusted(pad, pad, -pad, -pad)
        painter.drawRoundedRect(
            rect, task.icon_radius, task.icon_radius, Qt.RelativeSize
        )

        if state == State.Stopped:
            painter.setBrush(text_color)
            pad *= 3
            rect = pix.rect().adjusted(pad, pad, -pad, -pad)
            painter.drawRect(rect)
        elif state == State.Running:
            icon_text = str(remaining)

            font = QFont(task.font)
            font.setPixelSize(task.text_size * icon_size // 100)

            painter.setFont(font)
            painter.setPen(text_color)

            metrics = QFontMetrics(font)
            rect = metrics.tightBoundingRect(icon_text)
            bottom_left = rect.bottomLeft()
            x = (
                (width - rect.width()) / 2
                + task.text_x * width / 100
                - bottom_left.x()
            )
            y = (
                (height - rect.height()) / 2
                + task.text_y * height / 100
                - bottom_left.y()
            )
            pos = QPoint(x, height - y)
            painter.drawText(pos, icon_text)
    finally:
        painter.end()

    return QIcon(pix)
