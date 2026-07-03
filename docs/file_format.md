# Level Description File Format

A level description file consists of comments, blank lines, and lines with six fields.

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
* continuation

### Type for line

* normal
* thick
* dashed
* dotted
* thin
* crinkled

This specifies line style.

#### Structure for `crinkled`

There are four colon-separated subfields for `crinkled`:

* `crinkled` (literal)
* number of interpolated points in the segment: default 10
* "curviness" parameter: default 1.0; the larger, the higher the average deviation from a straight line.  1.0 means, roughly, that an interpolated point can be located anywhere (randomly, independently for both r and theta) in the circle spanning the previous and next interpolated points.  A value near 2 will make something that looks vaguely like a coastline.
* crinkle type (default: linear):
  * linear (made up of straight line segments)
  * quadratic (made up of quadratic splines)
  * cubic (made up of cubic splines)

If any of these is omitted, the previous value of that parameter will be retained, or the default if it has never been set.

### Type for door

* vertical
* horizontal
* vertical double
* horizontal double

This specifies door orientation.

### Arc

Arc is not yet implemented.

### Type for block

* solid
* white
* hatched
* solid_thin
* white_thin
* block_end

This specifies the fill; "thin" refers to the block outline stroke.

The `block_end` marker finishes a continued block.

### Type for cave

A `cave` is like a `block` but its edges are not straight lines.
The fill markers are all identical.

The `cave_end` marker finishes a continued cave.

The type field contains three colon-separated subfields:

#### Fill

Same as for `block`.
This cannot be omitted.

#### Interpolated points

Number of interpolated points in the segment: default 50.
If not specified, the last used value, or the default, will be used.

#### Curviness

Amount of average deviation from a straight line: default 0.15.
If not specified, the last used value, or the default, will be used.

### Type for ellipse

* solid
* white
* hatched
* solid_thin
* white_thin

These mean the same thing they do for block.
There is no continuation for an ellipse.

### Type for toilet

* vertical
* horizontal

In the dungeon this project was designed to make the maps for, there is
quite a lot of thought given to sanitation and food preparation.

### Text

Three of the fields have different meanings for a `Text` line:

* endx specifies the text to use, which cannot contain commas.
* endy specifies the font to use: `sans_serif` or `serif`.
* type specifies the text size in grid units.

### Seed

Only the `startx` field has meaning for a `Seed` line: it is used as the seed for Python's [random.seed()](https://docs.python.org/3/library/random.html#random.seed) function.
The default is `default`.
Leave the field empty (e.g. `seed,,...`) to generate non-repeatable pseudo-random values.
The field is treated as a string, so "0" or "0.0" are *not* falsy values; they are non-empty strings and therefore `True`, and each will produce a different repeatable set of pseudo-random values.
The seed can be reset at any time.

### Continuation

Only the `block` and the `cave` kind may be continued.
This is used to indicate that the polygon begun with the `cave` or `block` kind statement continues on the current line.
`block_end` or `cave_end`, respectively, as the `type` on the final line of the `block` or `cave` signals the end of the polygon.
