"""Test format conversion."""

import tempfile
from pathlib import Path

from svgmapper.services.converter import Converter


def test_convert() -> None:
    here = Path(__file__).parent
    data = here / "data"
    inp = data / "crypt.desc"
    reference = data / "output" / "crypt.svgmap"
    with tempfile.NamedTemporaryFile() as f:
        conv = Converter(inp=inp, output=Path(f.name))
        conv.convert_input()
        output = Path(f.name).read_text()
    ref_output = reference.read_text()
    assert output == ref_output
