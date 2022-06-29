import logging
import sys

from app.core.config import Config

logger = logging.getLogger()


def setup_logging(config: Config):
    logger.setLevel(config.LOG_LEVEL)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(config.LOG_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
