"""Create PDF from typst document."""

from pathlib import Path

import typst


class PDFCreator:
    """Create PDF from typst document."""

    def __init__(self, typst: Path, pdf: Path) -> None:
        self._typst = typst
        self._pdf = pdf

    def create(self) -> None:
        typst.compile(f"{self._typst!s}", output=f"{self._pdf!s}")
