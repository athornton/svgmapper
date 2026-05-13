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
    required=True,
    help="Input map file.",
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
def convert(*, file: Path, output: Path, debug: bool) -> None:
    """Convert from old-style ``makemap.pl`` input to current format."""
    svc = Converter(inp=file, output=output, debug=debug)
    svc.convert_input()


@click.option(
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
    required=True,
    help="Input map file.",
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
def create(*, file: Path, output: Path, settings: Path, debug: bool) -> None:
    """Create SVG from description file."""
    svc = Creator(inp=file, output=output, settings=settings, debug=debug)
    svc.create()
