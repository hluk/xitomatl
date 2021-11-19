#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.0-or-later
"""
Simple pomodoro timer app residing in tray.
"""
import argparse
import signal
import sys

from PySide6.QtCore import QCoreApplication, QSettings

from xitomatl import __version__
from xitomatl.app import App
from xitomatl.log import APP_ID, log


def main():
    # Force exit app on SIGINT.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    QCoreApplication.setOrganizationName(APP_ID)
    QCoreApplication.setApplicationName(APP_ID)
    QSettings.setDefaultFormat(QSettings.IniFormat)

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
            f"(default {QSettings().fileName()})"
        ),
    )
    args = parser.parse_args()

    if args.config:
        settings = QSettings(args.config, QSettings.IniFormat)
    else:
        settings = QSettings()

    log.debug("Config: %s", settings.fileName())

    app = App(sys.argv, settings)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
