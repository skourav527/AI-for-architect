## This component is responsible for parsing Markdown documents into sections
## based on headings. Each section contains a heading path and the corresponding text.
## It returns a list of ParsedSection objects, each representing a section of the document.
## It is used internally by the document ingestion pipeline to break down documents
## into manageable sections.
## Remember: The parser does not search anything. It only understands and
## organizes document structure.

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSection:
    heading: str
    text: str


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def parse_document(text: str) -> list[ParsedSection]:
    """Split Markdown by heading path; plain text is returned as one section."""
    heading_stack: list[tuple[int, str]] = []
    sections: list[ParsedSection] = []
    current: list[str] = []

    def flush() -> None:
        body = "\n".join(current).strip()
        if body:
            sections.append(
                ParsedSection(
                    heading=" > ".join(title for _, title in heading_stack),
                    text=body,
                )
            )
        current.clear()

    for line in text.splitlines():
        match = _HEADING.match(line)
        if not match:
            current.append(line)
            continue

        flush()
        level = len(match.group(1))
        heading_stack[:] = [
            item for item in heading_stack if item[0] < level
        ]
        heading_stack.append((level, match.group(2).strip()))

    flush()
    return sections

