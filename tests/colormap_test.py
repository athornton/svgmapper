"""Test that patterns reuse color serials."""

from pathlib import Path
from textwrap import dedent

from svgmapper.services.creator import Creator


def test_colormap(tmp_path: Path) -> None:
    """Test that patterns reuse color serials."""
    desc = dedent("""
    # Change to red
    color,red,,,,
    # Then back to default
    color,#1EAED0,,,,
    """)
    inp = tmp_path / "inp.svgmap"
    inp.write_text(desc)
    outp = tmp_path / "outp.svg"
    creator = Creator(inp=inp, output=outp)
    creator.create()
    out_text = outp.read_text()
    assert "hatch00" in out_text  # Original
    assert "hatch01" in out_text  # Red
    assert "hatch02" not in out_text  # Original-again reuses hatch00
