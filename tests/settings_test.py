"""Test SVG settings."""

import json
import tempfile
from pathlib import Path

from svgmapper.services.creator import Creator


def test_settings() -> None:
    here = Path(__file__).parent
    data = here / "data"
    inp = data / "output" / "crypt.svgmap"
    outp = data / "output" / "crypt-alt-settings.svg"
    settings = data / "settings.json"
    with tempfile.NamedTemporaryFile() as f:
        creator = Creator(inp=inp, output=Path(f.name), settings=settings)
    settings_obj = json.loads(settings.read_text())
    creator._settings.update(settings_obj)

    for k in (
        "scale",
        "color",
        "width_inches",
        "height_inches",
        "grid_size_x",
        "grid_size_y",
    ):
        assert getattr(creator._settings, k) == settings_obj[k]

        for j in (
            "grid_stroke",
            "wall_stroke",
            "thick_wall_stroke",
            "thin_stroke",
        ):
            assert round(getattr(creator._settings, j), 6) == round(
                settings_obj[j] * creator._settings.scale, 6
            )

    with tempfile.NamedTemporaryFile() as f:
        creator = Creator(inp=inp, output=Path(f.name), settings=settings)
        creator.create()
        assert Path(f.name).read_text() == outp.read_text()
