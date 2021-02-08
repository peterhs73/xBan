import logging
import sys

root_logger = logging.getLogger()

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Track uncaught exception to debug mode"""
    root_logger.error(
        "Exception Occurred\n", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = handle_exception
