"""Models for global settings."""

from dataclasses import dataclass

from ..._types import Number


@dataclass
class Settings:
    """Global settings."""

    scale: Number = 100
    color: str = "#1EAED0"  # Close to TSR Blue
    width_inches: Number = 7.5
    height_inches: Number = 7.5
    grid_size_x: Number = 30
    grid_size_y: Number = 30
    grid_stroke: Number = 0.008
    wall_stroke: Number = 0.05
    thick_wall_stroke: Number = 0.15
    thin_stroke: Number = 0.02
    round_digits: int = 2
    _scaled: bool = False

    def __post_init__(self) -> None:
        if self._scaled:
            return
        scale = self.scale
        self.grid_stroke *= scale
        self.wall_stroke *= scale
        self.thick_wall_stroke *= scale
        self.thin_stroke *= scale
        self._scaled = True
