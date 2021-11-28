#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.0-or-later
"""
Simple pomodoro timer app residing in tray.
"""
import argparse
import os
import signal
import sys

from PySide6.QtCore import QCoreApplication, QSettings

from xitomatl import __version__
from xitomatl.app import App
from xitomatl.config import (
    default_qml_path,
    default_settings_file,
    fallback_qml_path,
)
from xitomatl.log import APP_ID, init_debug_logging, init_logging, log


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help=(
            "set the configuration file path"
            f"(default {default_settings_file()})"
        ),
    )
    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="print debug information",
    )
    parser.add_argument(
        "-q",
        "--qml",
        type=str,
        help=(
            "Path to QML file defining the icon appearance"
            f"(default {default_qml_path()} or {fallback_qml_path()})"
        ),
    )
    return parser.parse_args()


def create_app():
    # Force exit app on SIGINT.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QCoreApplication.setOrganizationName(APP_ID)
    QCoreApplication.setApplicationName(APP_ID)
    QSettings.setDefaultFormat(QSettings.IniFormat)

    args = parse_args()

    if args.debug:
        init_debug_logging()
    else:
        init_logging()

    if args.qml is not None and not os.path.exists(args.qml):
        raise SystemExit(f"Error: QML file {args.qml!r} not found.")

    if args.config:
        settings = QSettings(args.config, QSettings.IniFormat)
    else:
        settings = QSettings()

    log.debug("Config: %s", settings.fileName())

    return App(sys.argv, settings, args.qml)


def main():
    app = create_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
