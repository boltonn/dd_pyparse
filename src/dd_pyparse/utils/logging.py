import logging
import os
from pathlib import Path
from sys import stdout

from loguru import logger

from dd_pyparse.schemas.settings import settings

DEFAULT_LOG_FORMAT = (
    "<level>{level: <8}</level> "
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>"
)
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def make_logger(
    file_path: Path = None, level: str = "INFO", rotation: str = "1 day", retention: str = "1 week", format: str = DEFAULT_LOG_FORMAT
):
    # logger.remove(0)

    if file_path is not None:
        logger.add(str(file_path), rotation=rotation, retention=retention, enqueue=True, backtrace=True, level=level.upper(), format=format)

    intercept_handler = InterceptHandler()
    # logging.basicConfig(handlers=[intercept_handler], level=level)
    # logging.root.handlers = [intercept_handler]
    logging.root.setLevel(level)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "fastapi",
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
    ]:
        if name not in seen:
            logging.getLogger(name).handlers = [intercept_handler]
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = False

    logger.configure(
        handlers=[{"sink": stdout, "serialize": False, "level": level.upper(), "backtrace": True, "enqueue": True, "format": format}]
    )

    return logger


logger = make_logger(  # noqa F811
    file_path=settings.log_file,
    level=settings.log_level,
)
