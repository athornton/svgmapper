"""Test SVG creation."""

import tempfile
from pathlib import Path
from textwrap import dedent

from svgmapper.services.creator import Creator


def test_create() -> None:
    here = Path(__file__).parent
    data = here / "data"
    inp = data / "output" / "crypt.svgmap"
    reference = data / "output" / "crypt.svg"
    with tempfile.NamedTemporaryFile() as f:
        creator = Creator(inp=inp, output=Path(f.name))
        creator.create()
        output = Path(f.name).read_text()
    ref_output = reference.read_text()
    assert output == ref_output


def test_create_crinkle() -> None:
    here = Path(__file__).parent
    data = here / "data"
    inp = data / "crinkle.svgmap"
    reference = data / "output" / "crinkle.svg"
    with tempfile.NamedTemporaryFile() as f:
        creator = Creator(inp=inp, output=Path(f.name))
        creator.create()
        output = Path(f.name).read_text()
    ref_output = reference.read_text()
    assert output == ref_output


def test_nonreproducible_seed(tmp_path: Path) -> None:
    desc = dedent("""
    # Test that nonreproducible seeds do not generate the same output.
    seed,,,,,
    # filled cave
    cave,12.0,12.0,15.0,12.0,solid:12:1.8
    continuation,15.0,12.0,15.0,15.0,solid
    continuation,15.0,15.0,12.0,15.0,solid
    continuation,12.0,15.0,12.0,12.0,solid
    continuation,12.0,12.0,12.0,12.0,cave_end
    """)
    infile = tmp_path / "irreproducible.svgmap"
    infile.write_text(desc)
    o1 = tmp_path / "o1.svg"
    o2 = tmp_path / "o2.svg"
    creator = Creator(inp=infile, output=o1)
    creator.create()
    creator = Creator(inp=infile, output=o2)
    creator.create()
    assert o1.read_text() != o2.read_text()
