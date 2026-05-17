# SVGMapper

This is a project to generate OSR-style maps similar to those found in
classic early AD&D modules, such as S1, G2, or A4.

The [map description file format](file_format.md) describes the input format.

The [settings](settings.md) document describes the global settings file, which can be used to alter the appearance of the map.

This is a refinement of an old project of mine called [makemap](../perl/makemap.pl), which used a [numeric description file](../tests/data/crypt.desc) rather than the slightly-more-readable current description format.

## Usage

### svgmapper
```
Usage: svgmapper [OPTIONS] COMMAND [ARGS]...

  Command-line interface for svgmapper.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  convert  Convert from old-style ``makemap.pl`` input to current format.
  create   Create SVG from description file.
  help     Show help for any command.
```

### svgmapper convert

```
Usage: svgmapper convert [OPTIONS]

  Convert from old-style ``makemap.pl`` input to current format.

Options:
  -d, --debug                   Enable debug logging
  -o, --output PATH             Output map file.  [required]
  -f, -i, --file, --input PATH  Input map file.  [required]
  -h, --help                    Show this message and exit.
```

### svgmapper create

```
Usage: svgmapper create [OPTIONS]

  Create SVG from description file.

Options:
  -s, --settings PATH           Global settings file
  -d, --debug                   Enable debug logging
  -o, --output PATH             Output map file.  [required]
  -f, -i, --file, --input PATH  Input map file.  [required]
  -h, --help                    Show this message and exit.
```

### Examples

These are from one of the levels of a dungeon I'm working on.

The [level description file](../tests/data/output/crypt.svgmap) was generated with `svgmapper convert` from the [old-format level description file](../tests/data/crypt.desc).

The [generated SVG](../tests/data/output/crypt.svg) was generated with `svg create` with the level description file as input.

![SVG Map](../tests/data/output/crypt.svg)

