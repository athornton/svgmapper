"""Convert from old-style to new-style format."""

from pathlib import Path

import structlog
from safir.logging import configure_logging

from ..exceptions import SVGBadInputError, SVGBadNumericInputError
from ..models.v1.input import (
    Block,
    Door,
    Line,
    MapObject,
    MapObjectKind,
    Text,
    Toilet,
)


class Converter:
    """Convert from old-style numeric format to new-style."""

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
        self._prev_kind: MapObjectKind | None = None
        self._prev_type: MapObject | float | None = None

    def convert_input(self) -> None:
        """Convert from old-style ``makemap.pl`` description file."""
        output: str = ""
        with self._input.open() as f:
            for raw_line in f:
                line = raw_line.strip()
                self._logger.debug(f"line: {line}")
                # Copy comments and blank lines
                if not line:
                    output += "\n"
                    continue
                if line.startswith("#"):
                    output += line + "\n"
                    continue
                new_line = self._convert_numeric(line)
                output += new_line + "\n"
        self._output.write_text(output)

    def _convert_numeric(self, line: str) -> str:
        try:
            obj_kind, startx, starty, endx, endy, obj_type = line.split(",")
        except ValueError as exc:
            raise SVGBadInputError(str(exc)) from exc
        try:
            i_o_kind = int(obj_kind)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(obj_kind)) from exc
        o_kind = MapObjectKind.from_int(i_o_kind)
        self._logger.debug(f"Object kind: {o_kind!s}")
        o_type = self._get_o_type(o_kind, endy, obj_type)
        try:
            (f_startx, f_starty) = (float(x) for x in (startx, starty))
        except ValueError as exc:
            raise SVGBadNumericInputError(str(exc)) from exc
        outline = f"{o_kind!s},{f_startx},{f_starty}"
        if o_kind == MapObjectKind.TEXT:
            font = self._get_font(endy)
            outline += f",{endx},{font}"
        else:
            try:
                f_endx, f_endy = (float(x) for x in (endx, endy))
            except ValueError as exc:
                raise SVGBadNumericInputError(str(exc)) from exc
            outline += f",{f_endx},{f_endy}"
        if o_kind != MapObjectKind.CONTINUATION:
            self._prev_kind = o_kind
        self._prev_type = o_type
        outline += f",{o_type}"
        return outline

    def _get_o_type(
        self, o_kind: MapObjectKind, endy: str, obj_type: str
    ) -> MapObject | float | None:
        o_type: MapObject | float | None = None
        match o_kind:
            case MapObjectKind.TEXT:
                o_type = self._get_o_type_text(obj_type)  # Font size
            case MapObjectKind.CONTINUATION:
                if self._prev_kind is None:
                    raise SVGBadInputError("Cannot continue unknown kind")
                if self._prev_type is None:
                    raise SVGBadInputError("Cannot continue unknown type")
                o_type = self._get_o_type(self._prev_kind, endy, obj_type)
            case _:
                try:
                    i_o_type = int(obj_type)
                except ValueError as exc:
                    raise SVGBadNumericInputError(str(obj_type)) from exc
                o_type = self._get_o_type_other(o_kind, i_o_type, obj_type)
        return o_type

    def _get_o_type_text(self, obj_type: str) -> float:
        try:
            return float(obj_type)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(obj_type)) from exc

    def _get_font(self, endy: str) -> str:
        try:
            if endy == "s":
                endy = "1"
            i_endy = int(endy)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(exc)) from exc
        return str(Text.from_int(i_endy))

    def _get_o_type_other(
        self, o_kind: MapObject, i_type: int, obj_type: str
    ) -> MapObject | None:
        match o_kind:
            case MapObjectKind.LINE:
                return Line.from_int(i_type)
            case MapObjectKind.ARC:
                raise NotImplementedError(str(o_kind))
            case MapObjectKind.DOOR:
                return Door.from_int(i_type)
            case MapObjectKind.BLOCK:
                return Block.from_int(i_type)
            case MapObjectKind.ELLIPSE:
                return None
            case MapObjectKind.SPIRAL_STAIRS:
                return None
            case MapObjectKind.TOILET:
                return Toilet.from_int(i_type)
            case _:
                raise NotImplementedError(str(o_kind))
