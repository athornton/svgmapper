"""Create PDF from typst document."""

from pathlib import Path

import typst


class PDFCreator:
    """Create PDF from typst document."""

    def __init__(self, typstfile: Path, pdf: Path) -> None:
        self._typst = typstfile
        self._pdf = pdf

    def create(self) -> None:
        typst.compile(self._typst, output=self._pdf, root=Path("/"))
