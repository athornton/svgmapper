"""Create SVG image from description file."""

import json
import math
from copy import deepcopy
from pathlib import Path

import svg
from svg import (
    Circle,
    Defs,
    Element,
    Ellipse,
    G,
    L,
    Length,
    M,
    Pattern,
    Point,
    Polygon,
    Rect,
    ViewBoxSpec,
)
from svg import Line as SVGLine
from svg import Path as SVGPath
from svg import Text as SVGText

from .._types import Number
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
from ..models.v1.settings import Settings
from ._base import BaseSVGMapper
from ._logger import configure_logging


class Creator(BaseSVGMapper):
    """Create SVG document from description file."""

    def __init__(
        self,
        inp: Path,
        output: Path,
        settings: Path | None = None,
        *,
        debug: bool = False,
    ) -> None:

        super().__init__(inp=inp, output=output, debug=debug)
        if settings:
            obj = json.loads(settings.read_text())
            self._settings = Settings(**obj)
        else:
            self._settings = Settings()
        self._logger = configure_logging("svgmapper.converter", debug=debug)
        self._prev_kind: MapObjectKind | None = None
        self._prev_type: MapObject | Number | None = None
        self._input_lines: list[str] = []
        self._current_block: list[tuple[int]] | None = None
        self._current_polygon: Polygon | None = None
        self._elements: list[Element] = []
        self._logger.debug("initialized")

    def create(self) -> None:
        """Create SVG from input."""
        lines = self._input.read_text().split("\n")
        self._input_lines = [x.strip() for x in lines]
        self._logger.debug(f"lines: {self._input_lines}")
        self._process_lines()

    def _process_lines(self) -> None:
        self._process_preamble()
        for line in self._input_lines:
            if not line:  # Skip blank lines
                self._logger.debug(f"L: {line}")
                continue
            if line.startswith("#"):
                self._logger.debug(f"L: {line}")
                continue  # Skip comments
            self._process_line(line)
        self._process_postamble()
        self._write_output()

    def _process_line(self, line: str) -> None:
        # Select processing method based on object kind.
        try:
            (obj_kind, startx, starty, endx, endy, obj_type) = line.split(",")
        except ValueError as exc:
            raise SVGBadInputError(str(exc)) from exc
        self._logger.debug(
            f"L: {obj_kind}, {startx}, {starty}, {endx}, {endy}, {obj_type}"
        )
        try:
            o_kind = MapObjectKind(obj_kind)
        except ValueError as exc:
            raise SVGBadInputError(str(exc)) from exc
        if o_kind == MapObjectKind.CONTINUATION:
            if self._prev_kind is None:
                raise SVGBadInputError("Cannot continue unknown kind")
        try:
            fstartx = float(startx)
            fstarty = float(starty)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(exc)) from exc
        x1 = fstartx * self._settings.scale
        y1 = fstarty * self._settings.scale
        if o_kind == MapObjectKind.TEXT:
            # Text is handled differently than all other objects.
            text = endx
            font = endy
            try:
                size = float(obj_type)
            except ValueError as exc:
                raise SVGBadNumericInputError(str(exc)) from exc
            self._process_text(x1, y1, text, font, size)
            return
        try:
            fendx = float(endx)
            fendy = float(endy)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(exc)) from exc
        x2 = fendx * self._settings.scale
        y2 = fendy * self._settings.scale
        self._process_svg_obj(o_kind, x1, y1, x2, y2, obj_type)

    def _process_svg_obj(
        self,
        o_kind: MapObjectKind,
        x1: Number,
        y1: Number,
        x2: Number,
        y2: Number,
        obj_type: str,
    ) -> None:
        match o_kind:
            case MapObjectKind.LINE:
                self._process_svgline(x1, y1, x2, y2, Line(obj_type))
            case MapObjectKind.ARC:
                raise NotImplementedError("Arc not implemented yet")
            case MapObjectKind.DOOR:
                self._process_door(x1, y1, x2, y2, Door(obj_type))
            case MapObjectKind.BLOCK:
                self._process_block(x1, y1, x2, y2, Block(obj_type))
            case MapObjectKind.ELLIPSE:
                self._process_ellipse(x1, y1, x2, y2, Block(obj_type))
            case MapObjectKind.SPIRAL_STAIRS:
                self._process_spiral_stairs(x1, y1, x2, y2)
            case MapObjectKind.TOILET:
                self._process_toilet(x1, y1, x2, y2, Toilet(obj_type))
            case MapObjectKind.CONTINUATION:
                self._process_continuation(x1, y1, x2, y2, obj_type)
            case _:
                raise SVGBadInputError(o_kind)
        if o_kind != MapObjectKind.CONTINUATION:
            self._prev_kind = o_kind

    def _process_preamble(self) -> None:
        self._makelib()
        self._makegrid()

    def _makelib(self) -> None:
        # Define reused symbols; just hatching for now.
        self._elements.append(Defs(elements=[self._makehatch()]))

    def _makehatch(self) -> Pattern:
        st = 0.25 * self._settings.scale
        return Pattern(
            id="hatch00",
            patternUnits="userSpaceOnUse",
            x=0,
            y=0,
            width=st,
            height=st,
            viewBox=ViewBoxSpec(min_x=0, min_y=0, width=st, height=st),
            elements=[self._makehatchgroup()],
        )

    def _makehatchgroup(self) -> G:
        st = 25
        cl = self._settings.color
        return G(
            elements=[
                SVGLine(x1=0, y1=0, x2=st, y2=st, stroke=cl, stroke_width=3)
            ],
        )

    def _makegrid(self) -> None:
        # Draw the map grid.
        sc = self._settings.scale
        cl = self._settings.color
        gx = self._settings.grid_size_x
        gy = self._settings.grid_size_y
        gs = self._settings.grid_stroke
        for yy in range(0, int(gy), int(sc)):
            for xx in range(0, int(gx), int(sc)):
                self._elements.append(
                    Rect(
                        height=sc,
                        width=sc,
                        stroke=cl,
                        stroke_width=gs,
                        x=xx,
                        y=yy,
                        fill="none",
                    )
                )

    def _process_postamble(self) -> None:
        pass

    def _process_svgline(
        self, x1: Number, y1: Number, x2: Number, y2: Number, style: Line
    ) -> None:
        sw = self._settings.wall_stroke
        da: list[Number] | None = None
        match style:
            case Line.THICK | Line.DOTTED:
                sw = self._settings.thick_wall_stroke
            case Line.THIN:
                sw = self._settings.thin_stroke
            case _:
                pass
        match style:
            case Line.DASHED:
                da = [
                    0.2 * self._settings.scale,
                    0.2 * self._settings.scale,
                ]
            case Line.DOTTED:
                da = [
                    0.1 * self._settings.scale,
                    0.15 * self._settings.scale,
                ]
            case _:
                pass

        self._elements.append(
            SVGPath(
                d=[
                    M(x1, y1),
                    L(x2, y2),
                ],
                stroke=self._settings.color,
                stroke_width=sw,
                stroke_dasharray=da,  # type:ignore [arg-type]
            )
        )

    def _process_door(
        self, x1: Number, y1: Number, x2: Number, y2: Number, style: Door
    ) -> None:
        sc = self._settings.scale
        sw = self._settings.wall_stroke
        cl = self._settings.color
        match style:
            case Door.VERTICAL:
                ht = 0.4 * sc
                wd = 0.2 * sc
                xx = x1 - (0.1 * sc)
                yy = y1 + (0.3 * sc)
            case Door.HORIZONTAL:
                ht = 0.2 * sc
                wd = 0.4 * sc
                xx = x1 + (0.3 * sc)
                yy = y1 - (0.1 * sc)
            case Door.VERTICAL_DOUBLE:
                ht = 0.3 * sc
                wd = 0.2 * sc
                xx = x1 - (0.1 * sc)
                yy = y1 + (0.2 * sc)
            case Door.HORIZONTAL_DOUBLE:
                ht = 0.2 * sc
                wd = 0.3 * sc
                xx = x1 + (0.2 * sc)
                yy = y1 + (0.1 * sc)
            case _:
                raise SVGBadInputError(style)
        self._elements.append(
            Rect(
                height=ht,
                width=wd,
                stroke=cl,
                stroke_width=sw,
                fill="white",
                x=xx,
                y=yy,
            )
        )

    def _process_block(
        self, x1: Number, y1: Number, x2: Number, y2: Number, style: Block
    ) -> None:
        sw = self._settings.wall_stroke
        cl = self._settings.color
        match style:
            case Block.SOLID:
                fill = cl
            case Block.WHITE:
                fill = "white"
            case Block.HATCHED:
                fill = "url(#hatch00)"
            case Block.SOLID_THIN:
                fill = cl
                sw = self._settings.thin_stroke
            case Block.WHITE_THIN:
                fill = "white"
                sw = self._settings.thin_stroke
            case Block.HATCHED_THIN:
                fill = "url(#hatch00)"
                sw = self._settings.thin_stroke
            case Block.POLYGON_END:
                fill = cl  # Not used
            case _:
                raise SVGBadInputError(style)

        if self._current_polygon is None:
            self._current_polygon = Polygon(
                stroke=cl, stroke_width=sw, fill=fill
            )

        self._block_add_points(x1, y1, x2, y2)

        if style == Block.POLYGON_END:
            self._close_block()

    def _block_add_points(
        self,
        x1: Number,
        y1: Number,
        x2: Number,
        y2: Number,
    ) -> None:
        if not self._current_polygon:
            return  # Won't happen.
        if self._current_polygon.points is None:
            self._current_polygon.points = []
        if len(self._current_polygon.points) > 0:
            last = self._current_polygon.points[-1]
            if (x1 != last.x) or (y1 != last.y):
                self._current_polygon.points.append(Point(x=x1, y=y1))
        else:
            self._current_polygon.points.append(Point(x=x1, y=y1))
        last = self._current_polygon.points[-1]  # There's at least one now.
        if (x2 != last.x) or (y2 != last.y):
            self._current_polygon.points.append(Point(x=x2, y=y2))

    def _close_block(self) -> None:
        if (
            (not self._current_polygon)
            or (self._current_polygon.points is None)
            or len(self._current_polygon.points) < 1
        ):
            return
        start = self._current_polygon.points[0]
        last = self._current_polygon.points[0]
        if (start.x != last.x) or (start.y != last.y):
            # Close the polygon.
            self._current_polygon.points.append(start)
        cp = deepcopy(self._current_polygon)
        self._elements.append(cp)
        self._current_polygon = None

    def _process_ellipse(
        self, x1: Number, y1: Number, x2: Number, y2: Number, style: Block
    ) -> None:
        sw = self._settings.wall_stroke
        cl = self._settings.color
        match style:
            case Block.SOLID:
                fill = cl
            case Block.WHITE:
                fill = "white"
            case Block.HATCHED:
                fill = "url(#hatch00)"
            case Block.SOLID_THIN:
                fill = cl
                sw = self._settings.thin_stroke
            case Block.WHITE_THIN:
                fill = "white"
                sw = self._settings.thin_stroke
            case Block.HATCHED_THIN:
                fill = "url(#hatch00)"
                sw = self._settings.thin_stroke
            case _:
                raise SVGBadInputError(style)
        self._elements.append(
            Ellipse(
                fill=fill,
                stroke=cl,
                stroke_width=sw,
                cx=x1,
                cy=y1,
                rx=x2,
                ry=y2,
            )
        )

    def _process_spiral_stairs(
        self, x1: Number, y1: Number, x2: Number, y2: Number
    ) -> None:
        sc = self._settings.scale
        cl = self._settings.color
        z = sc * math.sqrt(2) / 4.0
        sw = (self._settings.wall_stroke + self._settings.thin_stroke) / 2.0
        self._elements.append(
            Circle(
                cx=x1,
                cy=y1,
                r=sc / 2.0,
                fill="white",
                stroke=cl,
                stroke_width=sw,
            )
        )
        self._elements.append(
            SVGLine(
                x1=x1,
                y1=y1 + 0.5 * sc,
                x2=x1,
                y2=y1 - 0.5 * sc,
                stroke_width=sw,
                stroke=cl,
            )
        )
        self._elements.append(
            SVGLine(
                x1=x1 + 0.5 * sc,
                y1=y1,
                x2=x1 - 0.5 * sc,
                y2=y1,
                stroke_width=sw,
                stroke=cl,
            )
        )
        self._elements.append(
            SVGLine(
                x1=x1 + z,
                y1=y1 - z,
                x2=x1 - z,
                y2=y1 + z,
                stroke_width=sw,
                stroke=cl,
            )
        )
        self._elements.append(
            SVGLine(
                x1=x1 + z,
                y1=y1 + z,
                x2=x1 - z,
                y2=y1 - z,
                stroke_width=sw,
                stroke=cl,
            )
        )

    def _process_toilet(
        self, x1: Number, y1: Number, x2: Number, y2: Number, style: Toilet
    ) -> None:
        cl = self._settings.color
        sc = self._settings.scale
        sw = self._settings.thin_stroke
        drainsize = 0.03 * sc
        fill = "white"
        match style:
            case Toilet.VERTICAL:
                rx = 0.15 * sc
                ry = 0.2 * sc
                cx2 = x1
                cy2 = y1 - (0.05 * sc)
            case Toilet.HORIZONTAL:
                rx = 0.2 * sc
                ry = 0.15 * sc
                cx2 = x1 - (0.05 * sc)
                cy2 = y1
            case _:
                raise SVGBadInputError(style)
        self._elements.append(
            Ellipse(
                stroke=cl,
                stroke_width=sw,
                fill=fill,
                cx=x1,
                cy=y1,
                rx=rx,
                ry=ry,
            )
        )
        self._elements.append(
            Circle(
                stroke=cl,
                stroke_width=sw,
                fill=cl,
                cx=cx2,
                cy=cy2,
                r=drainsize,
            )
        )

    def _process_text(
        self, x1: Number, y1: Number, text: str, font: str, size: Number
    ) -> None:
        cl = self._settings.color
        sw = self._settings.thin_stroke
        sc = self._settings.scale
        fsize = Length(value=int(sc * size), unit="px")
        match font:
            case Text.SANS_SERIF:
                face = "HelveticaNeue-CondensedBold"
                family = "sans-serif"
                # Close to AD&D V1 modules: S1-3, G1-3, A1-4, etc.
            case Text.SERIF:
                face = "Soutane"
                family = "serif"
                # Close to X3-X4
            case _:
                raise SVGBadInputError(font)
        self._elements.append(
            SVGText(
                x=x1,
                y=y1,
                stroke=cl,
                stroke_width=sw,
                fill=cl,
                text=text,
                font_family=f"{face}, {family}",
                font_size=fsize,
            )
        )

    def _process_continuation(
        self, x1: Number, y1: Number, x2: Number, y2: Number, obj_type: str
    ) -> None:
        if self._prev_kind != MapObjectKind.BLOCK:
            raise SVGBadInputError(
                f"Can only continue Blocks, not {self._prev_kind}"
            )
        self._process_block(x1, y1, x2, y2, Block(obj_type))

    def _write_output(self) -> None:
        self._output.write_text(
            str(
                svg.SVG(
                    width=Length(value=self._settings.width_inches, unit="in"),
                    height=Length(
                        value=self._settings.height_inches, unit="in"
                    ),
                    viewBox=ViewBoxSpec(
                        min_x=0,
                        min_y=0,
                        width=self._settings.grid_size_x,
                        height=self._settings.grid_size_y,
                    ),
                    elements=self._elements,
                )
            )
        )
