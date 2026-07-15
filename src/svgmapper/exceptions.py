"""Exceptions for SVGMapper."""

from dataclasses import dataclass
from pathlib import Path
from typing import override


@dataclass
class SVGMapperError(Exception):
    """Base class for SVGMapper Errors."""

    message: str | None = None
    original_exception: Exception | None = None
    input_line: int | None = None
    input_file: Path | None = None
    current_line: str | None = None

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
        if self.input_file:
            msg += f" of file '{self.input_file}"
        if self.current_line:
            msg += f": '{self.current_line}'"
        return msg


class SVGBadInputError(SVGMapperError):
    """Malformed input."""


class SVGBadNumericInputError(SVGBadInputError):
    """Malformed numeric input."""
