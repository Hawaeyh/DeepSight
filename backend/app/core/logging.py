import sys

from loguru import logger

from app.core.config import settings


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DDTHH:mm:ss.SSSZ} | {level} | "
            "request_id={extra[request_id]} | {name}:{function}:{line} | {message}"
        ),
    )
    logger.configure(extra={"request_id": "-"})
