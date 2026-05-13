"""Base class for SVGMapper."""

from pathlib import Path

import structlog
from safir.logging import configure_logging


class BaseSVGMapper:
    """Base class that others inherit."""

    def __init__(
        self, inp: Path, output: Path, *, debug: bool = False
    ) -> None:
        self._input = inp
        self._output = output
        self._debug = debug
        loglevel = "info"
        if debug:
            loglevel = "debug"
        configure_logging(name="SVGMapper", log_level=loglevel)
        self._logger = structlog.getLogger("SVGMapper")
        self._logger.debug("Logging initialized")
