#!/usr/bin/env python3
from PySide6.QtGui import QColorConstants, QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

app = QGuiApplication()
svg = QSvgRenderer("xitomatl.svg")
image = QImage(128, 128, QImage.Format.Format_ARGB32)
image.fill(QColorConstants.Transparent)
painter = QPainter(image)
svg.render(painter)
painter.end()
image.save("xitomatl.png")
