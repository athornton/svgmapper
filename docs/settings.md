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

### Scale

Scale is the global scale that translates from grid units into pixels, I guess?
SVG is scalable, so the only place this matters is in displayed text; fractional font sizes do not seem to work well.

As the creator of a description file, you don't need to worry about it.
All the coordinate specification you do will be in terms of multiples of grid units.

### Color

These maps are monochrome.
This specifies the color of all elements.
The default is "#1EAED0", which is quite close to the blue used by TSR in the classic AD&D modules whose style this mapper is trying to emulate.

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
