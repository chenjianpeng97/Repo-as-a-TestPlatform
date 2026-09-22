"""Tiny YAML-subset front-matter reader/writer (no PyYAML dependency).

Supports what ``docs/spec/assets-knowledge-syntax.md`` and
``docs/spec/metadata-conventions.md`` need: scalar ``key: value`` pairs,
inline lists ``[a, b]``, inline maps ``{k: v}``, block lists (``- item``) and
one-or-more levels of indented block mappings. Comments (``# …``) are ignored.
Anything fancier (anchors, multi-line strings) is out of scope on purpose.
"""
from __future__ import annotations

import re
from typing import Any

FRONT_MATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)


def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return ``(front_matter_block, body)``; block is ``None`` when absent."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def parse_front_matter(text: str) -> dict[str, Any]:
    """Parse the leading ``---`` block of a Markdown file into a dict (``{}`` if none)."""
    block, _ = split_front_matter(text)
    if block is None:
        return {}
    return parse_yaml_block(block)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
def parse_yaml_block(block: str) -> dict[str, Any]:
    lines = [_strip_comment(line.rstrip("\r")) for line in block.splitlines()]
    lines = [line for line in lines if line.strip()]
    value, _ = _parse_mapping(lines, 0, _indent_of(lines[0]) if lines else 0)
    return value if isinstance(value, dict) else {}


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _strip_comment(line: str) -> str:
    if "#" not in line:
        return line
    out: list[str] = []
    quote: str | None = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            continue
        if ch == "#" and (not out or out[-1] in (" ", "\t")):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _parse_mapping(lines: list[str], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        line = lines[index]
        cur = _indent_of(line)
        if cur < indent:
            break
        if cur > indent:
            index += 1  # stray deeper line without key — skip defensively
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        key, sep, rest = stripped.partition(":")
        if not sep:
            index += 1
            continue
        key = key.strip().strip("'\"")
        rest = rest.strip()
        if rest:
            result[key] = parse_scalar(rest)
            index += 1
            continue
        # block value follows
        index += 1
        if index >= len(lines):
            result[key] = None
            break
        nxt = lines[index]
        nxt_indent = _indent_of(nxt)
        if nxt_indent <= indent:
            result[key] = None
            continue
        if nxt.strip().startswith("- "):
            value, index = _parse_list(lines, index, nxt_indent)
        else:
            value, index = _parse_mapping(lines, index, nxt_indent)
        result[key] = value
    return result, index


def _parse_list(lines: list[str], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(lines):
        line = lines[index]
        cur = _indent_of(line)
        if cur < indent or not line.strip().startswith("- "):
            break
        if cur > indent:
            index += 1
            continue
        body = line.strip()[2:].strip()
        if body and ":" in body and not body.startswith(("[", "{", "'", '"')) and not _looks_like_url(body):
            # "- key: value" → mapping item, possibly continued on deeper lines
            sub_lines = [" " * (indent + 2) + body]
            index += 1
            while index < len(lines) and _indent_of(lines[index]) > indent and not lines[index].strip().startswith("- "):
                sub_lines.append(lines[index])
                index += 1
            value, _ = _parse_mapping(sub_lines, 0, indent + 2)
            items.append(value)
            continue
        items.append(parse_scalar(body))
        index += 1
    return items, index


def _looks_like_url(text: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*://", text))


def parse_scalar(raw: str) -> Any:
    text = raw.strip()
    if text == "" or text in ("~", "null", "Null", "NULL"):
        return None
    if text in ("true", "True", "TRUE"):
        return True
    if text in ("false", "False", "FALSE"):
        return False
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        return [parse_scalar(part) for part in _split_top_level(inner)] if inner else []
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        out: dict[str, Any] = {}
        for part in _split_top_level(inner) if inner else []:
            key, sep, value = part.partition(":")
            if sep:
                out[key.strip().strip("'\"")] = parse_scalar(value)
        return out
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def _split_top_level(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    quote: str | None = None
    current: list[str] = []
    for ch in text:
        if quote:
            current.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if "".join(current).strip():
        parts.append("".join(current).strip())
    return parts


# ---------------------------------------------------------------------------
# Writer
# ---------------------------------------------------------------------------
def dump_front_matter(data: dict[str, Any]) -> str:
    """Serialize a dict into a ``---`` block (deterministic key order = insertion order)."""
    lines = ["---"]
    lines.extend(_dump_mapping(data, 0))
    lines.append("---")
    return "\n".join(lines) + "\n"


def _dump_mapping(data: dict[str, Any], indent: int) -> list[str]:
    pad = " " * indent
    out: list[str] = []
    for key, value in data.items():
        if isinstance(value, dict):
            if not value:
                out.append(f"{pad}{key}: {{}}")
                continue
            out.append(f"{pad}{key}:")
            out.extend(_dump_mapping(value, indent + 2))
        elif isinstance(value, (list, tuple)):
            if all(not isinstance(item, (dict, list, tuple)) for item in value):
                out.append(f"{pad}{key}: [{', '.join(_dump_scalar(item) for item in value)}]")
            else:
                out.append(f"{pad}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        sub = _dump_mapping(item, indent + 4)
                        if sub:
                            out.append(f"{pad}  - {sub[0].strip()}")
                            out.extend(sub[1:])
                    else:
                        out.append(f"{pad}  - {_dump_scalar(item)}")
        else:
            out.append(f"{pad}{key}: {_dump_scalar(value)}")
    return out


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    needs_quotes = (
        text == ""
        or text.strip() != text
        or any(ch in text for ch in ":#[]{},\"'")
        or text.lower() in {"true", "false", "null", "~", "yes", "no"}
        or re.fullmatch(r"-?\d+(\.\d+)?", text) is not None
    )
    if needs_quotes:
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def replace_front_matter(text: str, data: dict[str, Any]) -> str:
    """Return *text* with its front-matter replaced (or prepended) by *data*."""
    block, body = split_front_matter(text)
    rendered = dump_front_matter(data)
    if block is None:
        return rendered + ("\n" if body and not body.startswith("\n") else "") + body
    return rendered + body
