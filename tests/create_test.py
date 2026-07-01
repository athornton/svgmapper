"""Test SVG creation."""

import tempfile
from pathlib import Path

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
