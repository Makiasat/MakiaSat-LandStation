from loguru import logger
import sys

FORMAT = '<cyan>{time:DD-MM-YYYY - HH-MM-SS}</cyan> | <level>{level}</level> | <magenta>{module}</magenta>:<magenta>{function}</magenta>:<magenta>{line}</magenta> - <level>{message}</level>'


def setup_logger(log: logger, path: str):
    log.remove()
    log.add(
        sys.stdout,
        format=FORMAT
    )
    log.add(
        path,
        format=FORMAT
    )
    new_level = logger.level("SERIAL", no=38, color="<yellow>", icon="🐍")
    log.add(
        "serial_logger/{time}-serial.log",
        level="SERIAL",
        format="<cyan>{time:DD-MM-YYYY - HH-MM-SS}</cyan> | {message}"
    )

