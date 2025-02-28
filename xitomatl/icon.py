# SPDX-License-Identifier: LGPL-2.0-or-later
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import (
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)

from xitomatl.log import log
from xitomatl.state import State

unavailable_fonts = set()


def render_text(painter, task, size, icon_text):
    family, *style = task.font.split(";", maxsplit=1)
    family = family.strip()
    font = QFont(family)
    if not font.exactMatch() and family not in unavailable_fonts:
        unavailable_fonts.add(family)
        log.warning("Font is not available: %s", family)

    if style:
        font.setStyleName(style[0].strip())

    font.setPixelSize(task.text_size * size.width() // 100)

    metrics = QFontMetrics(font)
    rect = metrics.tightBoundingRect(icon_text)
    bottom_left = rect.bottomLeft()
    x = (
        (size.width() - rect.width()) / 2
        + task.text_x * size.width() / 100
        - bottom_left.x()
    )
    y = (
        (size.height() - rect.height()) / 2
        + task.text_y * size.height() / 100
        - bottom_left.y()
    )
    pos = QPoint(x, size.height() - y)

    if task.text_stroke_width > 0:
        path = QPainterPath()
        path.addText(pos, font, icon_text)
        stroke = QPen(
            task.text_stroke_color,
            task.text_stroke_width * size.width() // 100,
        )
        painter.strokePath(path, stroke)

    painter.setFont(font)
    painter.setPen(task.text_color)
    painter.drawText(pos, icon_text)


def task_icon(task, state, remaining_minutes, icon_size):
    """Created QPixmap for given task and state."""
    pix = QPixmap(icon_size, icon_size)
    pix.fill(Qt.transparent)
    try:
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        if state == State.Running:
            remaining = remaining_minutes
            if remaining <= 0:
                remaining = -remaining
                task = task.as_timed_out()

        painter.setPen(QPen(task.line_color, task.line_width * icon_size // 100))

        pad = task.icon_padding * icon_size // 100
        painter.setBrush(task.color)
        rect = pix.rect().adjusted(pad, pad, -pad, -pad)
        if task.image:
            image = QPixmap(task.image)
            if image.isNull():
                log.warning("Failed to load image: %s", task.image)
            else:
                painter.drawPixmap(rect, image)
        else:
            painter.drawRoundedRect(
                rect, task.icon_radius, task.icon_radius, Qt.RelativeSize
            )

        if state == State.Stopped:
            painter.setBrush(task.text_color)
            pad *= 3
            rect = pix.rect().adjusted(pad, pad, -pad, -pad)
            painter.drawRect(rect)
        elif state == State.Running:
            render_text(painter, task, pix.size(), str(remaining))
    finally:
        painter.end()

    return pix
