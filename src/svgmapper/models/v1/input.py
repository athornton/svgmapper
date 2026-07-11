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
    COLOR = "color"
    REGRID = "regrid"
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


class Arc(MapObject):
    """Arc (a portion of an ellipse)."""

    NORMAL = "normal"
    THICK = "thick"
    DASHED = "dashed"
    DOTTED = "dotted"
    THIN = "thin"

    # There was never an old-style "Arc" kind to convert from; although
    # defined, it was never used.


class Block(MapObject):
    """Filled block."""

    SOLID = "solid"
    WHITE = "white"
    HATCHED = "hatched"
    WAVE = "wave"
    SOLID_THIN = "solid_thin"
    WHITE_THIN = "white_thin"
    HATCHED_THIN = "hatched_thin"
    WAVE_THIN = "wave_thin"
    BLOCK_END = "block_end"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:  # Wave did not exist in the old style
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
                return cls.BLOCK_END
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Cave(MapObject):
    """Filled cave, with crinkled lines between points."""

    SOLID = "solid"
    WHITE = "white"
    HATCHED = "hatched"
    WAVE = "wave"
    SOLID_THIN = "solid_thin"
    WHITE_THIN = "white_thin"
    HATCHED_THIN = "hatched_thin"
    WAVE_THIN = "wave_thin"
    CAVE_END = "cave_end"

    # There was never an old-style "Cave" kind to convert from.


class Ellipse(MapObject):
    """Ellipse."""

    SOLID = "solid"
    WHITE = "white"
    HATCHED = "hatched"
    WAVE = "wave"
    SOLID_THIN = "solid_thin"
    WHITE_THIN = "white_thin"
    HATCHED_THIN = "hatched_thin"
    WAVE_THIN = "wave_thin"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:  # Wave did not exist in the old style.
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
            case _:
                raise SVGBadNumericInputError(f"{cls.__name__}: {number}")


class Door(MapObject):
    """Door."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
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


# SpiralStairs, Seed, Color, and Regrid are never actually used; they are
# just placeholders so that all fields in the input map to some object in the
# input model.


class SpiralStairs(MapObject):
    """Spiral Staircase."""

    # There are no variants of SpiralStairs.


class Toilet(MapObject):
    """Toilet. Seriously, there are a lot of these in the dungeon."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    VERTICAL_REVERSED = "vertical_reversed"
    HORIZONTAL_REVERSED = "horizontal_reversed"

    @override
    @classmethod
    def from_int(cls, number: int) -> Self:
        """Convert from old numeric representation."""
        match number:  # Only one orientation in old style
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

    # There was no prior seed kind to convert from.


class Color(MapObject):
    """Drawing color."""

    # There was no prior color kind to convert from.


class Regrid(MapObject):
    """Redraw the grid in a specified rectangle."""

    # There was no prior regrid kind to convert from.
