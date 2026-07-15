"""Document class for SVGMapper."""

from dataclasses import dataclass, field


@dataclass
class Document:
    """Document for creating typst."""

    title: list[str] = field(default_factory=list)
    right: list[str] = field(default_factory=list)
    key: list[str] = field(default_factory=list)
