"""Command-line interface."""

from pathlib import Path

import click
from safir.click import display_help

from .services.converter import Converter
from .services.creator import Creator

__all__ = ["convert", "help"]


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(message="%(version)s")
def main() -> None:
    """Command-line interface for svgmapper."""


@main.command()
@click.argument("topic", default=None, required=False, nargs=1)
@click.pass_context
def help(ctx: click.Context, topic: str | None) -> None:
    """Show help for any command."""
    display_help(main, ctx, topic)


@click.option(
    "--inp",
    "--file",
    "--input",
    "-f",
    "-i",
    envvar="SVGMAPPER_INPUT_PATH",
    type=click.Path(path_type=Path),
    required=True,
    help="Input map file.",
)
@click.option(
    "--output",
    "-o",
    envvar="SVGMAPPER_OUTPUT_PATH",
    type=click.Path(path_type=Path),
    default=None,
    help="Output map file.",
)
@click.option(
    "--debug",
    "-d",
    envvar="DEBUG",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@main.command()
def convert(*, inp: Path, output: Path, debug: bool) -> None:
    """Convert from old-style ``makemap.pl`` input to current format."""
    output = _check_output(inp, output)
    svc = Converter(inp=inp, output=output, debug=debug)
    svc.convert()


@click.option(
    "--inp",
    "--file",
    "--input",
    "-f",
    "-i",
    envvar="SVGMAPPER_INPUT_PATH",
    type=click.Path(path_type=Path),
    required=True,
    help="Input map file.",
)
@click.option(
    "--output",
    "-o",
    envvar="SVGMAPPER_OUTPUT_PATH",
    type=click.Path(path_type=Path),
    required=False,
    help="Output svg file.",
)
@click.option(
    "--typst",
    "-t",
    envvar="SVGMAPPER_TYPST_PATH",
    type=click.Path(path_type=Path),
    required=False,
    help="Output typst file.",
)
@click.option(
    "--pdf",
    "-p",
    envvar="SVGMAPPER_PDF_PATH",
    type=click.Path(path_type=Path),
    required=False,
    help="Output PDF file.",
)
@click.option(
    "--debug",
    "-d",
    envvar="DEBUG",
    is_flag=True,
    default=False,
    help="Enable debug logging",
)
@click.option(
    "--settings",
    "-s",
    envvar="SVGMAPPER_SETTINGS",
    type=click.Path(path_type=Path),
    help="Global settings file",
)
@main.command()
def create(
    *,
    inp: Path,
    output: Path | None,
    typst: Path | None,
    pdf: Path | None,
    settings: Path,
    debug: bool,
) -> None:
    """Create SVG from description file."""
    output = _check_output(inp, output)
    typst = _check_typst(inp, typst)
    pdf = _check_pdf(inp, pdf)

    svc = Creator(
        inp=inp,
        output=output,
        typst=typst,
        pdf=pdf,
        settings=settings,
        debug=debug,
    )
    svc.create()


# Helper functions


def _check_param(inp: Path, var: Path | None, ext: str) -> Path:
    if var is not None:
        return var
    return inp.parent / f"{inp.stem}.{ext}"


def _check_output(inp: Path, outp: Path | None) -> Path:
    return _check_param(inp, outp, "svg")


def _check_typst(inp: Path, outp: Path | None) -> Path:
    return _check_param(inp, outp, "typ")


def _check_pdf(inp: Path, outp: Path | None) -> Path:
    return _check_param(inp, outp, "pdf")
