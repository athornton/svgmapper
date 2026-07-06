# Global Settings File

A settings file may optionally be specified.
If it is not, default settings will be used.
If a settings file is used, then all settings must be specified.

## Settings

* `scale`
* `color`
* `width_inches`
* `height_inches`
* `grid_size_x`
* `grid_size_y`
* `grid_stroke`
* `wall_stroke`
* `thick_wall_stroke`
* `thin_stroke`
* `round_digits`

### Scale

Scale is the global scale that translates from grid units into something
close to pixels.
SVG is by definition scalable, so the only place this matters is in displayed text; fractional font sizes do not seem to work well.

As the creator of a description file, you don't need to worry about it.
All the coordinate specification you do will be in terms of multiples of grid units.

### Color

These maps are generally monochrome.
This specifies the color of all map elements.
The default is "#1EAED0", which is quite close to the blue used by TSR in the classic AD&D modules whose style this mapper is trying to emulate.

However, you can use the `color` directive to change the color of drawn elements at any point; at the start to draw the whole map in a different color, or in the middle to create multicolored maps.

### Sizes

The two fields `width_inches` and `height_inches` define how large the map should be in print or on-screen.
The default is a square 7.5 inches on a side.
This can be screen-captured, cropped, and then pasted into a [One-Page Dungeon template](https://www.dungeoncontest.com/classic-opd-template).

The fields `grid_size_x` and `grid_size_y` represent the number of grid squares in each dimension.
This defaults to 30 for both, again fitting the One Page Dungeon template.

### Strokes

The strokes are given in multiples of a grid unit.
The defaults are as follows:

* `grid_stroke`: 0.008
* `wall_stroke`: 0.05
* `thick_wall_stroke`: 0.15
* `thin_stroke`: 0.02

### Round_digits

This specifies how many decimal digits after the decimal point to retain for
interpolated points.
Interpolated points are only used in `crinkled` walls and in `cave` blocks.
Direct user input is always retained as-is.
The default is 2, which is plenty for 30 grid units and scale 100.

