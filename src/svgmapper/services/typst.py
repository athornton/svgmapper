"""Typst generator for SVGMapper."""

from pathlib import Path

from ..models.domain.document import Document


class TypstCreator:
    """Typst generator for SVGMapper."""

    def __init__(self, document: Document, typst: Path, svg: Path) -> None:
        self._document = document
        self._typst = typst
        self._svg = svg
        self._output: list[str] = []

    def create(self) -> None:
        """Create typst document."""
        self._make_preamble()
        self._make_title()
        self._make_midamble()
        self._make_key()
        self._write_output()

    def _make_preamble(self) -> None:
        preamble = [
            "#set page(",
            '    "us-letter",',
            "    margin: 1cm",
            ")",
            "#show title: set align(center)",
        ]
        self._output.extend(preamble)

    def _make_title(self) -> None:
        if self._document.title:
            self._output.extend(["#set document(", "    title: ["])
            self._output.extend(["        " + x for x in self._document.title])
            self._output.append("    ]")
        self._output.extend(
            [
                ")",
            ]
        )

    def _make_midamble(self) -> None:
        # Fix any embedded double quotes in name.
        svgstr = str(self._svg).replace('"', '\\"')
        self._output.extend(
            [
                "#set text(",
                '    font: "Helvetica Neue",',
                '    weight: "light",',
                "    size: 8pt",
                ")",
                "#set par(",
                "    leading: 0.3em",
                ")",
                '#set heading(numbering: "1.")',
            ]
        )
        if self._document.title:
            self._output.append("#title()")
        self._output.extend(
            [
                "#grid(",
                "    columns: (69%, 2%, 28%),",
                "    grid.cell(",
                "        image(",
                f'            "{svgstr}",',
                "             width: 100%",
                "        )",
                "    ),",
                "    grid.cell([]),",
            ]
        )
        if self._document.right:
            self._output.append("    grid.cell(")
            self._output.append("        [")

            for line in self._document.right:
                if line:
                    self._output.append("                " + line)
                else:
                    self._output.append("")
            self._output.append("        ]")
            self._output.append("    )")
        else:
            self._output.append("    grid.cell([])")
        self._output.append(")")

    def _make_key(self) -> None:
        if self._document.key:
            for line in self._document.key:
                self._output.append(line)

    def _write_output(self) -> None:
        self._typst.parent.mkdir(exist_ok=True, parents=True)
        self._typst.write_text("\n".join(self._output))
