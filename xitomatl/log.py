# SPDX-License-Identifier: LGPL-2.0-or-later
import logging

APP_ID = "pomodoro"

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format=f"%(asctime)s {APP_ID} %(levelname)s: %(message)s",
)
