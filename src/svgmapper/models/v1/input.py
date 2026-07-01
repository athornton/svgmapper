"""Model for input map file.

This also converts from the old-style ``makemap.pl`` map definition.
"""

from enum import StrEnum
from typing import Self, override

from ...exceptions import SVGBadNumericInputError


class MapObject(StrEnum):
    """Superclass for map objects."""

    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class MapObjectKind(MapObject):
    """Different kinds of map objects."""

    LINE = "line"
    ARC = "arc"
    DOOR = "door"
    BLOCK = "block"
    CAVE = "cave"
    ELLIPSE = "ellipse"
    SPIRAL_STAIRS = "spiral_stairs"
    TOILET = "toilet"
    TEXT = "text"
    SEED = "seed"
    CONTINUATION = "continuation"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 1:
                return cls.LINE
            case 2:
                return cls.ARC
            case 3:
                return cls.DOOR
            case 5:
                return cls.BLOCK
            case 6:
                return cls.ELLIPSE
            case 7:
                return cls.SPIRAL_STAIRS
            case 8:
                return cls.TOILET
            case 9:
                return cls.TEXT
            case 99:
                return cls.CONTINUATION
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Line(MapObject):
    """Line, usually representing a wall."""

    NORMAL = "normal"
    THICK = "thick"
    DASHED = "dashed"
    DOTTED = "dotted"
    THIN = "thin"
    CRINKLED = "crinkled"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 1:
                return cls.NORMAL
            case 2:
                return cls.THICK
            case 3:
                return cls.DASHED
            case 4:
                return cls.DOTTED
            case 5:
                return cls.THIN
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class CrinkleType(MapObject):
    """Different types of crinkles."""

    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUBIC = "cubic"


class Block(MapObject):
    """Filled block."""

    SOLID = "solid"
    WHITE = "white"
    HATCHED = "hatched"
    SOLID_THIN = "solid_thin"
    WHITE_THIN = "white_thin"
    HATCHED_THIN = "hatched_thin"
    POLYGON_END = "polygon_end"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 1:
                return cls.SOLID
            case 2:
                return cls.WHITE
            case 3:
                return cls.HATCHED
            case 5:
                return cls.SOLID_THIN
            case 6:
                return cls.WHITE_THIN
            case 7:
                return cls.HATCHED_THIN
            case 99:
                return cls.POLYGON_END
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Cave(MapObject):
    """Filled cave, with crinkled lines between points."""

    SOLID = "solid"
    WHITE = "white"
    HATCHED = "hatched"
    SOLID_THIN = "solid_thin"
    WHITE_THIN = "white_thin"
    HATCHED_THIN = "hatched_thin"
    CAVE_END = "cave_end"


class Door(MapObject):
    """Door."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizonal"
    VERTICAL_DOUBLE = "vertical_double"
    HORIZONTAL_DOUBLE = "horizontal_double"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 1:
                return cls.VERTICAL
            case 2:
                return cls.HORIZONTAL
            case 3:
                return cls.VERTICAL_DOUBLE
            case 4:
                return cls.HORIZONTAL_DOUBLE
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Toilet(MapObject):
    """Toilet. Seriously, there are a lot of these in the dungeon."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 1:
                return cls.VERTICAL
            case 2:
                return cls.HORIZONTAL
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Text(MapObject):
    """Text."""

    SANS_SERIF = "sans_serif"
    SERIF = "serif"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:
            case 0:
                return cls.SANS_SERIF
            case 1:
                return cls.SERIF
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Seed(MapObject):
    """Random Seed."""
