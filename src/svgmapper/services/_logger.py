"""Logger for SVGMapper classes."""

import logging
import sys


def configure_logging(name: str, *, debug: bool = False) -> logging.Logger:
    """Set up logging."""
    logger = logging.getLogger(name)
    logger.handlers = []
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(stream_handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.debug(f"Logging enabled for {name}")
    return logger
