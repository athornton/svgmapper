"""Exceptions for SVGMapper."""

from dataclasses import dataclass
from typing import override


@dataclass
class SVGMapperError(Exception):
    """Base class for SVGMapper Errors."""

    message: str | None = None
    original_exception: Exception | None = None
    input_line: int | None = None

    @override
    def __str__(self) -> str:
        msg = self.__class__.__name__
        if self.message:
            msg += f": {self.message}"
        if self.original_exception:
            msg += (
                f" from '{self.original_exception.__class__.__name__}:"
                f" {self.original_exception!s}'"
            )
        if self.input_line:
            msg += f" at input line {self.input_line}"
        return msg


class SVGBadInputError(SVGMapperError):
    """Malformed input."""


class SVGBadNumericInputError(SVGBadInputError):
    """Malformed numeric input."""
