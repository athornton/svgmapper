# Level Description File Format

A level description file consists of comments, blank lines, and lines
with six comma-separated fields.

## Fields

* kind
* startx
* starty
* endx
* endy
* type

A line starting with "#" is a comment line and is ignored during processing.
Blank lines are also ignored.

## Coordinates

The coordinates in `startx`, `starty`, `endx`, and `endy` are given in terms of map grid units.
The origin `(0,0)` is at the upper left.

## Kind

* line
* door
* arc
* block
* cave
* ellipse
* spiral_stairs
* toilet
* text
* seed
* color
* regrid
* continuation

### Type for line

* normal
* thick
* dashed
* dotted
* thin
* crinkled

This specifies line style.

#### Structure for `crinkled` type field

There are four colon-separated subfields when `crinkled` is the base type:

* `crinkled` (literal)
* number of interpolated points in the segment: default 10
* "curviness" parameter: default 1.0; the larger, the higher the average deviation from a straight line.  1.0 means, roughly, that an interpolated point can be located anywhere (randomly, independently for both `r` and `theta`) in the circle spanning the previous and next interpolated points.
A value near 2 will yield something that looks vaguely like a coastline.
* crinkle type (default: linear):
  * linear (made up of straight line segments)
  * quadratic (made up of quadratic splines)
  * cubic (made up of cubic splines)

If any of these is omitted, the previous value of that parameter will be retained, or the default if it has never been set.

### Door

The center of the door is at (`startx`,`starty`).
The `endx` and `endy` parameters for a door are ignored, and are conventionally set to `0`.

#### Type for door

* vertical
* horizontal
* vertical double
* horizontal double

This specifies door orientation and whether it is a single or double door.

### Structure for `Arc` type field

There are six colon-separated fields for the `Arc` type field:

* style
  * normal
  * thick
  * dashed
  * dotted
  * thin
* x-radius
* y-radius
* rotation
* large_arc
* sweep

The `style` field has the same meaning as for `Line`.
`x-radius` and `y-radius` are the radius of the ellipse from which the arc is taken.
If omitted, half the distance between the start and end points (for each coordinate) is used.
If the specified radius is too small, the ellipse radius will be expanded as necessary to make the arc physically realizable.
`rotation` is the arc's rotation in degrees.
If omitted, the rotation is `0`.
Set `large_arc` and/or `sweep` to truthy values to declare that the arc goes the long way around and, roughly, whether to make the arc concave rather than convex with respect to its endpoints.
See the [SVG Documentation for Arcs](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorials/SVG_from_scratch/Paths#arcs) for more information.

### Type for block

* solid
* white
* hatched
* wave
* solid_thin
* white_thin
* hatched_thin
* wave_thin
* block_end

This specifies the fill; "thin" refers to the block outline stroke.

The `block_end` marker finishes a continued block.

### Type for cave

A `cave` is like a `block` but its edges are not straight lines.
The fill markers are all identical.

The `cave_end` marker finishes a continued cave.

#### Structure for `Cave` type field.

The type field contains three colon-separated subfields:

##### Fill

Same as for `block`.
This cannot be omitted.

##### Interpolated points

Number of interpolated points in the segment: default 10.
If not specified, the last used value, or the default, will be used.
This is the same as for a crinkled line.

##### Curviness

Amount of average deviation from a straight line: default 1.0.
If not specified, the last used value, or the default, will be used.
This is the same as for a crinkled line.

### Type for ellipse

* solid
* white
* hatched
* wave
* solid_thin
* white_thin
* hatched_thin
* wave_thin

These mean the same thing they do for block.
The center of the ellipse is at (`startx`,`starty`).
The `endx` and `endy` coordinates are the x-radius and y-radius of the ellipse, respectively.
There is no continuation for an ellipse.

### Spiral stairs

The center of the spiral staircase is at (`startx`,`starty`) and its radius is half a grid unit, so if you want the staircase to sit neatly in a grid cell, make those half-integers.
The `endx` and `endy` coordinates must be present but are ignored; `0` is the conventional value to use.

### Type for toilet

* vertical
* horizontal
* vertical_reversed
* horizontal_reversed

In the dungeon this project was designed to make the maps for, there is
quite a lot of thought given to sanitation and food preparation.

The center of the toilet bowl is at (`startx`,`starty`).
The "reversed" versions have the drain towards the bottom and the right, respectively, of the center of the bowl.

### Text

The text begins at (`startx`,`starty`).

Three of the fields have different meanings for a `Text` line:

* endx specifies the text to use, which cannot contain commas.
* endy specifies the font to use: `sans_serif` or `serif`.
* type specifies the text size in grid units.

### Seed

Only the `startx` field has meaning for a `Seed` line: it is used as the seed for Python's [random.seed()](https://docs.python.org/3/library/random.html#random.seed) function.
The default is `default`.
Leave the field empty (e.g. `seed,,...`) to generate non-repeatable pseudo-random values.
The field is treated as a string, and therefore Python's rules for seeding use the code path for strings, not numbers.
However, before doing this, an attempt is made to test whether the seed, when interpreted as a number, would be equivalent to zero.
That means that `0` or `0.0` would yield falsy values, and therefore be nonreproducible.
The seed can be reset at any time.

### Color

Only the `startx` field has meaning for a `Color` line.
It changes the color of drawn objects to the value of the field.
Any legal CSS color can be used; named colors and RGB hexadecimal are probably the most common.
The exception to this is that the field cannot contain a comma, so the `light-dark` colors will not work.
Color can be reset at any time.

### Regrid

It is sometimes useful to redraw the map grid.
One common example is when you're drawing an irregular cave on a solid background.
The easiest way to do that is to draw a solid rectangle, then draw the cave with white fill on top of it.
As soon as you drew the solid rectangle, though, you obliterated the grid.
Thus, after you draw the cave, you will want to use `regrid` to redraw the grid in the rectangle whose corners are at (`startx`,`starty`) and (`endx`,`endy`).
The grid will include the entire bounding box (that is, both coordinate ranges are closed, rather than the more usual half-open), which means that a regrid that is m*n in size will draw m+1 vertical lines and n+1 horizontal lines.

### Continuation

Only the `block` and the `cave` kind may be continued.
This is used to indicate that the polygon begun with the `cave` or `block` kind statement continues on the current line.
It is necessary because `block` or `cave` may represent extremely complicated shapes.
`block_end` or `cave_end`, respectively, as the `type` on the final line of the `block` or `cave` signals the end of the polygon.
