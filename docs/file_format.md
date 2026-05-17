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
* ellipse
* spiral_stairs
* toilet
* text
* continuation

### Type for line

* normal
* thick
* dashed
* dotted
* thin

This specifies line style.

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
