# SPDX-License-Identifier: LGPL-2.0-or-later
import os
from functools import lru_cache

from PySide6.QtCore import QSettings

QML_FILENAME = "xitomatl.qml"


@lru_cache(maxsize=None)
def default_settings_file():
    return QSettings().fileName()


def default_qml_path():
    default_settings_dir = os.path.dirname(default_settings_file())
    return os.path.join(default_settings_dir, QML_FILENAME)


def fallback_qml_path():
    main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(main_dir, "resources", QML_FILENAME)
