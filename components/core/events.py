import logging
from typing import Callable

log = logging.getLogger("uvicorn")


def create_start_app_handler() -> Callable:
    def start_app():
        log.info("Server Start >>>>>")
    return start_app


def create_stop_app_handler() -> Callable:
    def stop_app():
        log.info("Server End >>>>>")
    return stop_app
