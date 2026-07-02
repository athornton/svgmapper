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
* number of interpolated points in the segment: default 50
* "curviness" parameter: default 0.15; the larger, the higher the average deviation from a straight line
* crinkle type (default: linear):
  * linear (made up of straight line segments)
  * quadratic (made up of quadratic splines)
  * cubic (made up of cubic splines)

### Type for door

* vertical
* horizontal
* vertical double
* horizontal double

This specifies door orientation

### Type for block

* solid
* white
* hatched
* solid_thin
* white_thin
* polygon_end

This specifies the fill; "thin" refers to the block outline stroke.

The `polygon_end` marker finishes a continued block.

### Type for cave

A `cave` is like a `block` but its edges are not straight lines.

The `cave_end` marker finishes a continued cave.

The type field contains three colon-separated subfields:

#### Fill

Same as for `block`.

#### Interpolated points

Number of interpolated points in the segment: default 50.

#### Curviness

Amount of average deviation from a straight line: default 0.15.

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
* endy specifies the font to use: "s" means use Soutane font (serif).
* type specifies the text size in grid units.

### Seed

Only the `startx` field has meaning for a `Seed` line: it is used as the seed for Python's [random.seed()](https://docs.python.org/3/library/random.html#random.seed) function.
The default is `default`.
Leave the field empty (e.g. `seed,,...`) to generate non-repeatable pseudo-random values.
It may be helpful to experiment with different values and then keep the one that produces the most pleasing outcome.
The seed can be reset at any time.

### Continuation

Only the `block` and the `cave` kind may be continued.
This is used to indicate that the polygon begun with the `cave` or `block` kind statement continues on the current line.
`block_end` or `cave_end`, respectively, as the `type` on the final line of the `block` or `cave` signals the end of the polygon.
