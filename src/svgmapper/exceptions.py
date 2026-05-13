"""Exceptions for SVGMapper."""


class SVGMapperError(Exception):
    """Base class for SVGMapper Errors."""


class SVGBadInputError(SVGMapperError):
    """Malformed input."""


class SVGBadNumericInputError(SVGBadInputError):
    """Malformed numeric input."""
