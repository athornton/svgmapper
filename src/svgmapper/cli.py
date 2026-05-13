"""Command-line interface."""

from pathlib import Path

import click
from safir.click import display_help

from .services.svgmapper import SVGMapper

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
    "--input",
    "-i",
    envvar="SVGMAPPER_INPUT_PATH",
    type=click.Path(path_type=Path),
    default=None,
    help="Input map file.",
)
@click.option(
    "--output",
    "-o",
    envvar="SVGMAPPER_OUTPUT_PATH",
    type=click.Path(path_type=Path),
    default=None,
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
def convert(*, input: Path, output: Path, debug: bool) -> None:  # noqa: A002
    """Convert from old-style ``makemap.pl`` input to current format."""
    svc = SVGMapper(inp=input, output=output, debug=debug)
    svc.convert_input()
