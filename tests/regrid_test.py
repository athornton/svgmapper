"""Test regrid."""

from pathlib import Path
from textwrap import dedent

import pytest

from svgmapper.exceptions import SVGBadNumericInputError
from svgmapper.services.creator import Creator


def _dedesc(inp: Path) -> list[str]:
    # Strip `<desc>` entries from SVG
    r: list[str] = []
    with inp.open() as f:
        while ln := f.readline():
            if ln.find("<desc>") == -1:
                r.append(ln)
    return r


def test_regrid(tmp_path: Path) -> None:
    """Test regrid by permuting coordinates and validating integer input."""
    blockdesc = dedent("""
    # Big white block
    block,2,2,2,28,white
    continuation,2,28,28,28,white
    continuation,28,28,28,2,white
    continuation,28,2,2,2,block_end
    """)

    n = 0
    for x in (2, 28):
        for y in (2, 28):
            x2 = 2 if x == 28 else 28
            y2 = 2 if y == 28 else 28
            inp = tmp_path / f"input{n}.svgmap"
            regrid = f"regrid,{x},{y},{x2},{y2},"
            inp.write_text(blockdesc + "\n" + regrid + "\n")
            n += 1
    for n in range(4):
        outp = tmp_path / f"output{n}.svg"
        creator = Creator(inp=(tmp_path / f"input{n}.svgmap"), output=outp)
        creator.create()

    ref = tmp_path / "output0.svg"
    # We use dedesc because although the lines drawn are identical, the
    # description shows different coordinates for the (2,28),(28,2) and the
    # (2,2),(28,2) cases.
    expected = _dedesc(ref)
    for n in range(1, 4):
        actual = _dedesc(tmp_path / f"output{n}.svg")
        assert actual == expected

    (tmp_path / "bad.svgmap").write_text(
        blockdesc + "\n" + "regrid,2,2,28,28.3,\n"
    )
    creator = Creator(inp=tmp_path / "bad.svgmap", output=tmp_path / "xxx")
    with pytest.raises(SVGBadNumericInputError):
        creator.create()
