"""Create SVG image from description file.

This is the map generation engine.  It takes an input file described in
docs/file_format.md and generates an SVG.  With the default settings, a map
generated in this way will look like it belongs in a TSR D&D or AD&D module
from the late 1970s.
"""

import json
import math
import random
import urllib.parse
import xml.dom.minidom
from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import svg
from svg import Arc as SVGArc
from svg import (
    C,
    Circle,
    Defs,
    Desc,
    Element,
    G,
    L,
    Length,
    M,
    PathData,
    Pattern,
    Point,
    Polygon,
    Q,
    Rect,
    ViewBoxSpec,
)
from svg import Ellipse as SVGEllipse
from svg import Line as SVGLine
from svg import Path as SVGPath
from svg import Text as SVGText

from .._types import Number
from ..exceptions import (
    SVGBadInputError,
    SVGBadNumericInputError,
    SVGMapperError,
)
from ..models.v1.input import (
    Arc,
    Block,
    Cave,
    CrinkleType,
    Door,
    Line,
    MapObjectKind,
    Text,
    Toilet,
)
from ..models.v1.settings import Settings
from ._base import BaseSVGMapper


@dataclass
class _CubicControlPoints:
    c1: Point
    c2: Point


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
        self._prev_kind: MapObjectKind | None = None
        self._input_lines: list[str] = []
        self._current_polygon: Polygon | None = None
        self._pattern_serial = 0
        self._colormap: dict[str, str] = {
            self._settings.color: f"{self._pattern_serial:02d}"
        }
        self._num_points: int = 10
        self._curviness: Number = 1.0
        self._crinkle_type: CrinkleType = CrinkleType.LINEAR
        self._seed: str | None = "default"
        random.seed(self._seed)  # For repeatability
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
            self._logger.debug(f"L: {line}")
            if not line:  # Skip blank lines
                continue
            san_line = urllib.parse.quote(line, safe="=#/:, ")
            self._elements.append(Desc(text=san_line))
            if san_line.startswith("#"):
                continue  # Skip comments
            self._process_line(san_line)
        self._process_postamble()
        self._write_output()

    def _process_line(self, line: str) -> None:
        # Select processing method based on object kind.
        try:
            (obj_kind, startx, starty, endx, endy, obj_type) = line.split(",")
        except ValueError as exc:
            raise SVGBadInputError(str(exc)) from exc
        self._logger.debug(
            f"P: {obj_kind}, {startx}, {starty}, {endx}, {endy}, {obj_type}"
        )
        try:
            o_kind = MapObjectKind(obj_kind)
        except ValueError as exc:
            raise SVGBadInputError(str(exc)) from exc
        if o_kind == MapObjectKind.CONTINUATION:
            if self._prev_kind is None:
                raise SVGBadInputError("Cannot continue unknown kind")
        if o_kind == MapObjectKind.SEED:
            seed_t: float | str = startx
            # We use the string value for the seed, *except* that if it can
            # be converted into a zero-equivalent float, that becomes
            # falsy, therefore None, therefore nonreproducible.
            try:
                seed_t = float(startx)
            except ValueError:
                seed_t = startx
            seed = startx if seed_t else None  # Back to the string version
            self._seed = seed  # All falsy seeds are nonreproducible
            random.seed(self._seed)
            return
        if o_kind == MapObjectKind.COLOR:
            # Don't convert to numeric values; the first parameter is a
            # color specification (it cannot include a comma).
            self._settings.color = startx
            self._updatelib()  # Make a new hatch with the new color
            return
        try:
            fstartx = float(startx)
            fstarty = float(starty)
        except ValueError as exc:
            raise SVGBadNumericInputError(str(exc)) from exc
        x1 = fstartx * self._settings.scale
        y1 = fstarty * self._settings.scale
        if o_kind == MapObjectKind.TEXT:
            # Text is handled differently than most other objects.
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
                self._process_svgline(x1, y1, x2, y2, obj_type)
            case MapObjectKind.ARC:
                self._process_arc(x1, y1, x2, y2, obj_type)
            case MapObjectKind.DOOR:
                self._process_door(x1, y1, x2, y2, Door(obj_type))
            case MapObjectKind.BLOCK:
                self._process_block(x1, y1, x2, y2, Block(obj_type))
            case MapObjectKind.CAVE:
                self._process_cave(x1, y1, x2, y2, obj_type)
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
        # Define reused symbols
        self._elements.append(
            Defs(elements=[self._makehatch(), self._makewave()])
        )

    def _updatelib(self) -> None:
        # If we need to update reused symbols...
        cl = self._settings.color
        if cl not in self._colormap:
            self._pattern_serial += 1
            self._colormap[cl] = f"{self._pattern_serial:02d}"
            self._makelib()

    def _hatch(self) -> str:
        return f"url(#hatch{self._colormap[self._settings.color]})"

    def _wave(self) -> str:
        return f"url(#wave{self._colormap[self._settings.color]})"

    def _makehatch(self) -> Pattern:
        st = 0.25 * self._settings.scale
        return Pattern(
            id=f"hatch{self._colormap[self._settings.color]}",
            patternUnits="userSpaceOnUse",
            x=0,
            y=0,
            width=st,
            height=st,
            viewBox=ViewBoxSpec(min_x=0, min_y=0, width=st, height=st),
            elements=[self._makehatchgroup()],
        )

    def _makewave(self) -> Pattern:
        st = 0.25 * self._settings.scale
        return Pattern(
            id=f"wave{self._colormap[self._settings.color]}",
            patternUnits="userSpaceOnUse",
            x=0,
            y=0,
            width=st,
            height=st,
            viewBox=ViewBoxSpec(min_x=0, min_y=0, width=st, height=st),
            elements=[self._makewavegroup()],
        )

    def _makehatchgroup(self) -> G:
        st = 0.25 * self._settings.scale
        cl = self._settings.color
        return G(
            elements=[
                SVGLine(
                    x1=0,
                    y1=0,
                    x2=st,
                    y2=st,
                    stroke=cl,
                    stroke_width=0.03 * self._settings.scale,
                )
            ],
        )

    def _makewavegroup(self) -> G:
        st = 0.25 * self._settings.scale
        cl = self._settings.color
        elements: list[PathData] = []
        for i in range(4):
            x = round(st * (i % 2) / 2, self._settings.round_digits)
            y = round(i / 2 * st, self._settings.round_digits)
            begin = M(x, y)
            arcs = [
                SVGArc(
                    rx=0.2 * self._settings.scale,
                    ry=0.1 * self._settings.scale,
                    angle=0,
                    large_arc=False,
                    sweep=False,
                    x=round(x + st * j, self._settings.round_digits),
                    y=round(y, self._settings.round_digits),
                )
                for j in range(3)
            ]
            elements.append(begin)
            elements.extend(arcs)

        return G(
            elements=[
                SVGPath(
                    d=elements,
                    stroke=cl,
                    stroke_width=0.03 * self._settings.scale,
                    fill=None,
                )
            ]
        )

    def _makegrid(self) -> None:
        # Draw the map grid.
        sc = self._settings.scale
        cl = self._settings.color
        gx = self._settings.grid_size_x
        gy = self._settings.grid_size_y
        gs = self._settings.grid_stroke
        grid: list[PathData] = []
        for yy in range(1 + int(gy)):
            grid.append(M(0, yy * sc))
            grid.append(L(gx * sc, yy * sc))
        for xx in range(1 + int(gx)):
            grid.append(M(xx * sc, 0))
            grid.append(L(xx * sc, gy * sc))
        self._elements.append(Desc(text="# Map grid"))
        self._elements.append(
            SVGPath(
                d=grid,
                stroke=cl,
                stroke_width=gs,
            )
        )

    def _process_postamble(self) -> None:
        # Currently there is no postamble added.
        pass

    def _process_svgline(
        self, x1: Number, y1: Number, x2: Number, y2: Number, sstyle: str
    ) -> None:
        if sstyle.startswith(Line.CRINKLED):
            parts = sstyle.split(":")
            style = Line.CRINKLED
            subfields = len(parts)
            if subfields > 3:
                try:
                    self._crinkle_type = CrinkleType(parts[3].lower())
                except ValueError as exc:
                    raise SVGBadInputError(f"Bad crinkle type: {exc}") from exc
            if subfields > 2:
                try:
                    self._curviness = float(parts[2])
                    if self._curviness < 0:
                        raise SVGBadNumericInputError(
                            f"Bad curviness: {self._curviness}"
                        )
                except ValueError as exc:
                    raise SVGBadNumericInputError(
                        f"Bad curviness: {exc}"
                    ) from exc
            if subfields > 1:
                try:
                    self._num_points = int(parts[1])
                    if self._num_points < 2:
                        raise SVGBadNumericInputError(
                            "Bad number of interpolated points:"
                            f" {self._num_points}"
                        )
                except ValueError as exc:
                    raise SVGBadNumericInputError(
                        f"Bad number of interpolated points: {exc}"
                    ) from exc
        else:
            style = Line(sstyle)

        da: list[Number] | None = None
        match style:
            case Line.THICK | Line.DOTTED:
                sw = self._settings.thick_wall_stroke
            case Line.THIN:
                sw = self._settings.thin_stroke
            case _:
                sw = self._settings.wall_stroke
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

        if style == Line.CRINKLED:
            ipoints = self._make_squiggle_points(x1, y1, x2, y2)
            self._logger.debug(f"ipoints: len={len(ipoints)}, {ipoints}")

            path_elements: list[PathData] = [M(x1, y1)]

            for i in range(self._num_points):
                match self._crinkle_type:
                    case CrinkleType.QUADRATIC:
                        control_point = self._make_quadratic_control_point(
                            start=ipoints[i], end=ipoints[i + 1]
                        )
                        path_elements.append(
                            Q(
                                control_point.x,
                                control_point.y,
                                ipoints[i + 1].x,
                                ipoints[i + 1].y,
                            )
                        )
                    case CrinkleType.CUBIC:
                        cc = self._make_cubic_control_points(
                            start=ipoints[i], end=ipoints[i + 1]
                        )
                        path_elements.append(
                            C(
                                cc.c1.x,
                                cc.c1.y,
                                cc.c2.x,
                                cc.c2.y,
                                ipoints[i + 1].x,
                                ipoints[i + 1].y,
                            )
                        )
                    case _:  # linear
                        path_elements.append(
                            L(ipoints[i + 1].x, ipoints[i + 1].y)
                        )
            self._elements.append(
                SVGPath(
                    d=path_elements,
                    stroke=self._settings.color,
                    stroke_width=sw,
                    stroke_dasharray=da,  # type:ignore [arg-type]
                    fill="none",
                )
            )
        else:
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

    def _make_intermediate_points(
        self,
        x1: Number | Decimal,
        y1: Number | Decimal,
        x2: Number | Decimal,
        y2: Number | Decimal,
    ) -> list[Point]:
        num_points = self._num_points
        points = [Point(x1, y1)]
        x_delta = Decimal(x2) - Decimal(x1)
        y_delta = Decimal(y2) - Decimal(y1)
        points.extend(
            [
                Point(
                    Decimal(x1) + x_delta * Decimal(i / num_points),
                    Decimal(y1) + y_delta * Decimal(i / num_points),
                )
                for i in range(1, num_points)
            ]
        )
        points.append(Point(x2, y2))
        return points

    def _make_squiggle_points(
        self,
        x1: Number | Decimal,
        y1: Number | Decimal,
        x2: Number | Decimal,
        y2: Number | Decimal,
    ) -> list[Point]:
        intermediates = self._make_intermediate_points(x1, y1, x2, y2)
        scale = (
            self._distance(Point(x1, y1), Point(x2, y2))
            * self._curviness
            / (len(intermediates) - 1)
        )
        squiggle_points = [intermediates[0]]
        squiggle_points.extend(
            [self._make_perturbed_point(p, scale) for p in intermediates[1:-1]]
        )
        squiggle_points.append(intermediates[-1])
        return squiggle_points

    def _make_perturbed_point(
        self, p: Point, scale: Number | None = None
    ) -> Point:
        prec = self._settings.round_digits
        max_radius = (
            scale
            if scale is not None
            else self._settings.scale * self._curviness
        )
        r = random.random() * max_radius
        theta = random.random() * 2 * math.pi
        x = round(Decimal(p.x) + Decimal(r * math.cos(theta)), prec)
        y = round(Decimal(p.y) + Decimal(r * math.sin(theta)), prec)
        q = Point(x, y)
        self._logger.debug(
            f"PERTURB: Input: x={p.x:.2f}, y={p.y:.2f},"
            f" scale={scale} -> r={r:.2f}, theta={theta:.2f},"
            f" Output: x={q.x:.2f}, y={q.y:.2f}"
        )
        return q

    def _distance(self, a: Point, b: Point) -> Number:
        return math.sqrt(
            (Decimal(a.x) - Decimal(b.x)) * (Decimal(a.x) - Decimal(b.x))
            + (Decimal(a.y) - Decimal(b.y)) * (Decimal(a.y) - Decimal(b.y))
        )

    def _make_quadratic_control_point(self, start: Point, end: Point) -> Point:
        x1 = start.x
        y1 = start.y
        x2 = end.x
        y2 = end.y
        midpoint = Point(
            (Decimal(x1) + Decimal(x2)) / 2, (Decimal(y1) + Decimal(y2)) / 2
        )
        scale = self._curviness * self._distance(start, end)
        p = self._make_perturbed_point(midpoint, scale)
        self._logger.debug(
            f"QUADRATIC CONTROL POINT: p1: {start}, p2: {end}"
            f" midpoint: {midpoint},"
            f" control_point: {p}"
        )
        return p

    def _make_cubic_control_points(
        self, start: Point, end: Point
    ) -> _CubicControlPoints:
        x1 = start.x
        y1 = start.y
        dx = Decimal(end.x) - Decimal(start.x)
        dy = Decimal(end.y) - Decimal(start.y)
        scale = self._distance(start, end) * self._curviness / 6
        otpoint = Point(
            Decimal(x1) + Decimal(dx) / 3, Decimal(y1) + Decimal(dy) / 3
        )
        ttpoint = Point(
            Decimal(x1) + 2 * Decimal(dx) / 3,
            Decimal(y1) + 2 * Decimal(dy) / 3,
        )
        p = self._make_perturbed_point(otpoint, scale)
        q = self._make_perturbed_point(ttpoint, scale)
        self._logger.debug(
            f"CUBIC CONTROL POINTS: p1: {start}, p2: {end}"
            f" 1/3: {otpoint}, 2/3 {ttpoint}"
            f" first control point: {p}, second control point: {q}"
        )
        return _CubicControlPoints(c1=p, c2=q)

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
                yy = y1 - (0.1 * sc)
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
        if style in (Door.VERTICAL_DOUBLE, Door.HORIZONTAL_DOUBLE):
            if style == Door.VERTICAL_DOUBLE:
                yy += 0.3 * sc
            else:
                xx += 0.3 * sc
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

    def _process_arc(
        self, x1: Number, y1: Number, x2: Number, y2: Number, tstyle: str
    ) -> None:
        sw = self._settings.wall_stroke

        parts = tstyle.split(":")
        style = Arc(parts[0].lower())
        subfields = len(parts)
        sweep_flag = False
        large_arc_flag = False
        dx = (x2 - x1) / 2
        dy = (y2 - y1) / 2
        rotation = 0.0
        if subfields > 5:
            try:
                sweep_flag_t: float | str = float(parts[5])
            except ValueError:
                sweep_flag_t = parts[5]
            sweep_flag = bool(sweep_flag_t)
            self._logger.debug(f"Sweep {sweep_flag}")
        if subfields > 4:
            try:
                large_arc_flag_t: float | str = float(parts[4])
            except ValueError:
                large_arc_flag_t = parts[4]
            large_arc_flag = bool(large_arc_flag_t)
            self._logger.debug(f"Large Arc {large_arc_flag}")
        if subfields > 3:
            try:
                rotation = float(parts[3])
            except ValueError as exc:
                raise SVGBadNumericInputError(f"Bad rotation: {exc}") from exc
        if subfields > 2:
            try:
                dy = float(parts[2])
            except ValueError as exc:
                raise SVGBadNumericInputError(f"Bad y-radius: {exc}") from exc
        if subfields > 1:
            try:
                dx = float(parts[1])
            except ValueError as exc:
                raise SVGBadNumericInputError(f"Bad x-radius: {exc}") from exc

        da: list[Number] | None = None
        match style:
            case Line.THICK | Line.DOTTED:
                sw = self._settings.thick_wall_stroke
            case Line.THIN:
                sw = self._settings.thin_stroke
            case _:
                sw = self._settings.wall_stroke
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

        path_elements = [
            M(x1, y1),
            SVGArc(
                rx=dx,
                ry=dy,
                angle=rotation,
                large_arc=large_arc_flag,
                sweep=sweep_flag,
                x=x2,
                y=y2,
            ),
        ]
        self._elements.append(
            SVGPath(
                d=path_elements,
                stroke=self._settings.color,
                stroke_width=sw,
                stroke_dasharray=da,  # type:ignore [arg-type]
                fill="none",
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
                fill = self._hatch()
            case Block.WAVE:
                fill = self._wave()
            case Block.SOLID_THIN:
                fill = cl
                sw = self._settings.thin_stroke
            case Block.WHITE_THIN:
                fill = "white"
                sw = self._settings.thin_stroke
            case Block.HATCHED_THIN:
                fill = self._hatch()
                sw = self._settings.thin_stroke
            case Block.WAVE_THIN:
                fill = self._wave()
                sw = self._settings.thin_stroke
            case Block.BLOCK_END:
                fill = cl  # Not used
            case _:
                raise SVGBadInputError(style)

        if self._current_polygon is None:
            self._current_polygon = Polygon(
                stroke=cl, stroke_width=sw, fill=fill
            )

        self._block_add_points(x1, y1, x2, y2)

        if style == Block.BLOCK_END:
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
            raise SVGMapperError("No block to close")
        self._logger.debug(
            f"CLOSE_BLOCK current polygon: {self._current_polygon}"
            f" len={len(self._current_polygon.points)}"
        )
        start = self._current_polygon.points[0]
        last = self._current_polygon.points[-1]
        self._logger.debug(f"start={start}, last={last}")
        if (start.x != last.x) or (start.y != last.y):
            # Close the polygon.
            if self._prev_kind == MapObjectKind.BLOCK:
                self._current_polygon.points.append(start)
            else:
                self._current_polygon.points.extend(
                    self._make_squiggle_points(
                        Decimal(start.x),
                        Decimal(start.y),
                        Decimal(last.x),
                        Decimal(last.y),
                    )[1:-1]
                )
        cp = deepcopy(self._current_polygon)
        self._elements.append(cp)
        self._current_polygon = None

    def _process_cave(
        self, x1: Number, y1: Number, x2: Number, y2: Number, tstyle: str
    ) -> None:
        sw = self._settings.wall_stroke
        cl = self._settings.color
        parts = tstyle.split(":")
        style = Cave(parts[0].lower())
        subfields = len(parts)
        if subfields > 2:
            try:
                self._curviness = float(parts[2])
                if self._curviness < 0:
                    raise SVGBadNumericInputError(
                        f"Bad curviness: {self._curviness}"
                    )
            except ValueError as exc:
                raise SVGBadNumericInputError(f"Bad curviness: {exc}") from exc
        if subfields > 1:
            try:
                self._num_points = int(parts[1])
                if self._num_points < 2:
                    raise SVGBadNumericInputError(
                        "Bad number of interpolated points:"
                        f" {self._num_points}"
                    )
            except ValueError as exc:
                raise SVGBadNumericInputError(
                    f"Bad number of interpolated points: {exc}"
                ) from exc
        self._logger.debug(
            f"CAVE: {style!s}, n={self._num_points}, c={self._curviness}"
        )
        match style:
            case Cave.SOLID:
                fill = cl
            case Cave.WHITE:
                fill = "white"
            case Cave.HATCHED:
                fill = self._hatch()
            case Cave.WAVE:
                fill = self._wave()
            case Cave.SOLID_THIN:
                fill = cl
                sw = self._settings.thin_stroke
            case Cave.WHITE_THIN:
                fill = "white"
                sw = self._settings.thin_stroke
            case Cave.HATCHED_THIN:
                fill = self._hatch()
                sw = self._settings.thin_stroke
            case Cave.WAVE_THIN:
                fill = self._wave()
                sw = self._settings.thin_stroke
            case Cave.CAVE_END:
                fill = cl  # Not used
            case _:
                raise SVGBadInputError(style)

        self._logger.debug(f"CAVE style {style}")

        if self._current_polygon is None:
            self._current_polygon = Polygon(
                stroke=cl, stroke_width=sw, fill=fill
            )

        self._cave_add_points(x1, y1, x2, y2)

        if style == Cave.CAVE_END:
            self._close_block()

    def _cave_add_points(
        self,
        x1: Number,
        y1: Number,
        x2: Number,
        y2: Number,
    ) -> None:
        if x1 != x2 or y1 != y2:
            self._logger.debug(
                f"CAVE add_points: x1: {x1:.2f} y1: {y1: .2f} x2: {x2:.2f}"
                f" y2: {y2:.2f}"
            )
            endarray = self._make_squiggle_points(x1, y1, x2, y2)
        else:
            endarray = [Point(x1, y1)]
        self._logger.debug(f"CAVE add_points SQUIGGLES: {endarray}")
        if not self._current_polygon:
            return  # Won't happen.
        self._logger.debug("CAVE add_points: polygon not None")
        if not self._current_polygon.points:
            self._current_polygon.points = endarray
        else:
            self._current_polygon.points.extend(endarray)
        self._logger.debug(
            f"CAVE add_points: polygon: {self._current_polygon.points}"
        )

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
                fill = self._hatch()
            case Block.WAVE:
                fill = self._wave()
            case Block.SOLID_THIN:
                fill = cl
                sw = self._settings.thin_stroke
            case Block.WHITE_THIN:
                fill = "white"
                sw = self._settings.thin_stroke
            case Block.HATCHED_THIN:
                fill = self._hatch()
                sw = self._settings.thin_stroke
            case Block.WAVE_THIN:
                fill = self._wave()
                sw = self._settings.thin_stroke
            case _:
                raise SVGBadInputError(style)
        self._elements.append(
            SVGEllipse(
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
            case Toilet.VERTICAL_REVERSED:
                rx = 0.15 * sc
                ry = 0.2 * sc
                cx2 = x1
                cy2 = y1 + (0.05 * sc)
            case Toilet.HORIZONTAL_REVERSED:
                rx = 0.2 * sc
                ry = 0.15 * sc
                cx2 = x1 + (0.05 * sc)
                cy2 = y1
            case _:
                raise SVGBadInputError(style)
        self._elements.append(
            SVGEllipse(
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
        if self._prev_kind not in (MapObjectKind.BLOCK, MapObjectKind.CAVE):
            raise SVGBadInputError(
                f"Can only continue Blocks and Caves, not {self._prev_kind}"
            )
        match self._prev_kind:
            case MapObjectKind.BLOCK:
                self._process_block(x1, y1, x2, y2, Block(obj_type))
            case MapObjectKind.CAVE:
                self._process_cave(x1, y1, x2, y2, obj_type)
            case _:
                pass

    def _write_output(self) -> None:
        svgstr = str(
            svg.SVG(
                width=Length(value=self._settings.width_inches, unit="in"),
                height=Length(value=self._settings.height_inches, unit="in"),
                viewBox=ViewBoxSpec(
                    min_x=0,
                    min_y=0,
                    width=self._settings.grid_size_x,
                    height=self._settings.grid_size_y,
                ),
                elements=self._elements,
            )
        )
        node = xml.dom.minidom.parseString(svgstr)
        pretty = node.toprettyxml()
        self._output.write_text(str(pretty))
