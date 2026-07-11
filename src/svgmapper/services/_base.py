"""Base class for SVGMapper."""

from pathlib import Path
from typing import Never

import structlog
from safir.logging import configure_logging

from ..exceptions import SVGBadInputError, SVGMapperError


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
        self._input_line: int = 0
        self._logger.debug("Logging initialized")

    def _raise(self, exc: Exception) -> Never:
        """Raise error, annotating with input line."""
        if isinstance(exc, SVGMapperError):
            exc.input_line = self._input_line
            raise exc
        err = SVGBadInputError(
            message=str(exc),
            input_line=self._input_line,
            original_exception=exc,
        )
        raise err from exc
