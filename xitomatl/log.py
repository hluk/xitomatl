# SPDX-License-Identifier: LGPL-2.0-or-later
import logging

APP_ID = "xitomatl"

log = logging.getLogger(__name__)


def init_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )


def init_debug_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format=f"%(asctime)s {APP_ID} %(levelname)s: %(message)s",
    )
