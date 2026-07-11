"""Test error reporting."""

from pathlib import Path
from textwrap import dedent

import pytest

from svgmapper.exceptions import SVGBadInputError, SVGBadNumericInputError
from svgmapper.services.converter import Converter
from svgmapper.services.creator import Creator


def test_errors(tmp_path: Path) -> None:
    """Test error reporting."""
    desc = dedent(
        """# Line 2 has an error: coordinates are not numeric
        line,2,2,4,twentyeight,normal
        """
    )
    inp = tmp_path / "input.svgmap"
    inp.write_text(desc)

    creator = Creator(inp=inp, output=tmp_path / "xxx")
    with pytest.raises(
        SVGBadNumericInputError,
        match=(
            "SVGBadNumericInputError"
            " from 'ValueError: could not convert string to float:"
            " 'twentyeight'' at input line 2"
        ),
    ):
        creator.create()
    desc = dedent(
        """# Line 2 has an error: "goofy" is not a line style
        line,2,2,4,28,goofy
        """
    )
    inp.write_text(desc)
    creator = Creator(inp=inp, output=tmp_path / "xxx")
    with pytest.raises(
        SVGBadInputError,
        match=(
            "SVGBadInputError from 'ValueError: 'goofy' is not a valid Line'"
            " at input line 2"
        ),
    ):
        creator.create()
    desc = dedent(
        """# Line 2 has an error: too few fields
        line,2,2,4,28
        """
    )
    inp.write_text(desc)
    creator = Creator(inp=inp, output=tmp_path / "xxx")
    with pytest.raises(
        SVGBadInputError,
        match=(
            "SVGBadInputError from 'ValueError: not enough values"
            " to unpack \\(expected 6, got 5\\)' at input line 2"
        ),
    ):
        creator.create()


def test_convert_errors(tmp_path: Path) -> None:
    desc = dedent(
        """# Line 2 has an error: Arc (type 2) was never implemented in perl
        2,3,4,6,6,0
        """
    )
    inp = tmp_path / "input.svgmap"
    inp.write_text(desc)

    converter = Converter(inp=inp, output=tmp_path / "xxx")
    with pytest.raises(
        SVGBadInputError,
        match=(
            "SVGBadInputError: arc from 'NotImplementedError: arc'"
            " at input line 2"
        ),
    ):
        converter.convert()

    desc = dedent(
        """# Line 2 has an error: there is no type 37
        37,3,4,6,6,0
        """
    )
    inp.write_text(desc)

    converter = Converter(inp=inp, output=tmp_path / "xxx")
    with pytest.raises(SVGBadInputError, match="MapObjectKind: 37"):
        converter.convert()
