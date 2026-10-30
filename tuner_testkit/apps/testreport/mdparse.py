"""Markdown helpers shared by the testsheet parser and the report renderer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_SEPARATOR_CELL_RE = re.compile(r"^:?-+:?$")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Flat ``key: value`` front-matter. Nested YAML values are kept as raw text."""

    text = normalize(text)
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    meta: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        if not line.strip() or line[0] in " \t#":
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, text[match.end():]


def heading(line: str) -> tuple[int, str] | None:
    match = _HEADING_RE.match(line)
    if not match:
        return None
    return len(match.group(1)), match.group(2).strip()


def split_row(line: str) -> list[str]:
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|") and not raw.endswith("\\|"):
        raw = raw[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", raw)]


def is_separator(line: str) -> bool:
    if "-" not in line:
        return False
    cells = split_row(line)
    return bool(cells) and all(_SEPARATOR_CELL_RE.match(cell.replace(" ", "")) for cell in cells)


@dataclass
class Table:
    header: list[str]
    rows: list[list[str]]
    headings: dict[int, str]
    line: int
    row_lines: list[int] = field(default_factory=list)

    def column(self, name: str) -> int | None:
        for idx, cell in enumerate(self.header):
            if cell == name:
                return idx
        return None

    def records(self) -> list[dict[str, str]]:
        out = []
        for row in self.rows:
            out.append({name: (row[idx] if idx < len(row) else "") for idx, name in enumerate(self.header)})
        return out


@dataclass
class Section:
    level: int
    title: str
    lines: list[str]
    line: int

    @property
    def text(self) -> str:
        return "\n".join(self.lines).strip()


def tables(body: str) -> list[Table]:
    lines = normalize(body).split("\n")
    found: list[Table] = []
    headings: dict[int, str] = {}
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        head = heading(line)
        if head:
            level, title = head
            headings = {k: v for k, v in headings.items() if k < level}
            headings[level] = title
            idx += 1
            continue
        if line.lstrip().startswith("|") and idx + 1 < len(lines) and is_separator(lines[idx + 1]):
            table = Table(header=split_row(line), rows=[], headings=dict(headings), line=idx + 1)
            idx += 2
            while idx < len(lines) and lines[idx].lstrip().startswith("|"):
                table.rows.append(split_row(lines[idx]))
                table.row_lines.append(idx + 1)
                idx += 1
            found.append(table)
            continue
        idx += 1
    return found


def sections(body: str, level: int) -> list[Section]:
    """Split ``body`` at headings of exactly ``level``; deeper headings stay in the text."""

    out: list[Section] = []
    current: Section | None = None
    for idx, line in enumerate(normalize(body).split("\n"), start=1):
        head = heading(line)
        if head and head[0] <= level:
            if current is not None:
                out.append(current)
            current = Section(level=head[0], title=head[1], lines=[], line=idx) if head[0] == level else None
            continue
        if current is not None:
            current.lines.append(line)
    if current is not None:
        out.append(current)
    return out


_NUMBER_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\s+")


def strip_number(title: str) -> str:
    return _NUMBER_PREFIX_RE.sub("", title).strip()


@dataclass
class Block:
    kind: str
    text: str = ""
    table: Table | None = None


def _para_blocks(lines: list[str]) -> list[Block]:
    if not lines[0].lstrip().startswith(("- ", "* ")):
        return [Block("para", " ".join(line.strip() for line in lines))]
    items = bullets("\n".join(lines))
    return [Block("para", item) for item in items]


def outline(body: str) -> dict[str, list[Block]]:
    """Each heading's own paragraphs and tables, keyed by title without its number prefix."""

    lines = normalize(body).split("\n")
    out: dict[str, list[Block]] = {"": []}
    key = ""
    para: list[str] = []

    def flush() -> None:
        if para:
            out[key].extend(_para_blocks(para))
            para.clear()

    idx = 0
    while idx < len(lines):
        line = lines[idx]
        head = heading(line)
        if head:
            flush()
            key = strip_number(head[1])
            out.setdefault(key, [])
            idx += 1
            continue
        if line.lstrip().startswith("|") and idx + 1 < len(lines) and is_separator(lines[idx + 1]):
            flush()
            table = Table(header=split_row(line), rows=[], headings={}, line=idx + 1)
            idx += 2
            while idx < len(lines) and lines[idx].lstrip().startswith("|"):
                table.rows.append(split_row(lines[idx]))
                table.row_lines.append(idx + 1)
                idx += 1
            out[key].append(Block("table", table=table))
            continue
        if line.strip():
            para.append(line)
        else:
            flush()
        idx += 1
    flush()
    return out


def bullets(text: str) -> list[str]:
    items: list[str] = []
    for line in normalize(text).split("\n"):
        stripped = line.strip()
        if stripped.startswith(("- ", "* ")):
            items.append(stripped[2:].strip())
        elif stripped and items and line.startswith((" ", "\t")):
            items[-1] += " " + stripped
    return items


def paragraphs(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", normalize(text).strip())
    return [" ".join(part.strip() for part in block.split("\n")).strip() for block in blocks if block.strip()]


def strip_images(text: str) -> tuple[str, list[str]]:
    images = [match.group(2) for match in _IMAGE_RE.finditer(text)]
    cleaned = _IMAGE_RE.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned).strip()
    return cleaned, images


def links(text: str) -> list[tuple[str, str]]:
    return [(m.group(1), m.group(2)) for m in _LINK_RE.finditer(text) if not text[max(m.start() - 1, 0)] == "!"]


def plain(text: str) -> str:
    """Drop images, unwrap links and inline code for prose that goes into Word."""

    cleaned, _ = strip_images(text)
    cleaned = _LINK_RE.sub(lambda m: m.group(1), cleaned)
    cleaned = cleaned.replace("**", "")
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"<br\s*/?>", "\n", cleaned, flags=re.I)
    return cleaned.strip()
