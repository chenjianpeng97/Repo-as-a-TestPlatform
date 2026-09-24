"""Structural checks for the functional testcase tree."""

from __future__ import annotations

import re
from pathlib import Path

from tuner_testkit.catalog.front_matter import parse_front_matter, split_front_matter

CASE_HEADING = re.compile(
    r"^#### ([A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*)(\d{4}) (正向|反向)-(\S.*)$"
)
ID_PREFIX = re.compile(r"^[A-Z][A-Za-z]*(?:-[A-Z][A-Za-z]*)*$")
STEP_BULLET = re.compile(r"^- 步骤：\S")
EXPECT_BULLET = re.compile(r"^- 预期：\S")
_HEADING = re.compile(r"^(#{1,6}) (.+)$", re.M)


def validate_tree(root: Path) -> list[str]:
    """Return human-readable errors. Empty list means the tree matches the spec."""
    root = root.resolve()
    errors: list[str] = []
    if not root.is_dir():
        return [f"{root}: assets/testcases directory is missing"]

    index = root / "README.md"
    if not index.is_file():
        errors.append(f"{_rel(index)}: module index README.md is required")
    else:
        errors.extend(_check_kind(index, "testcase-index"))

    seen: dict[str, str] = {}
    prefixes: dict[str, str] = {}
    modules = sorted(path for path in root.iterdir() if path.is_dir() and not path.name.startswith("."))
    for module in modules:
        errors.extend(_check_module(module, seen, prefixes))
    for path in root.iterdir():
        if path.is_file() and path.name != "README.md":
            errors.append(f"{_rel(path)}: only README.md belongs at the testcases root")
    return errors


def _check_module(module: Path, seen: dict[str, str], prefixes: dict[str, str]) -> list[str]:
    errors: list[str] = []
    readme = module / "README.md"
    if not readme.is_file():
        errors.append(f"{_rel(readme)}: module README.md is required")
    else:
        errors.extend(_check_kind(readme, "testcase-module"))

    feature_names: list[str] = []
    for path in sorted(module.iterdir()):
        if path.is_dir():
            errors.append(f"{_rel(path)}: do not nest directories under a module")
            continue
        if path.name == "README.md":
            continue
        if path.suffix.lower() != ".md":
            errors.append(f"{_rel(path)}: module files must be README.md or <feature>.md")
            continue
        feature_names.append(path.stem)
        errors.extend(_check_feature(path, module.name, seen, prefixes))

    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for name in feature_names:
            if name not in text:
                errors.append(f"{_rel(readme)}: feature list must mention {name}")
    return errors


def _check_feature(
    path: Path, module_name: str, seen: dict[str, str], prefixes: dict[str, str]
) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    rel = _rel(path)
    if meta.get("kind") != "testcase":
        errors.append(f"{rel}: front-matter kind must be testcase")
    if meta.get("module") != module_name:
        errors.append(f"{rel}: front-matter module must be {module_name}")
    if meta.get("title") != path.stem:
        errors.append(f"{rel}: front-matter title must be {path.stem}")
    prefix = str(meta.get("id_prefix") or "")
    if not ID_PREFIX.match(prefix):
        errors.append(f"{rel}: front-matter id_prefix must look like User-Login")
    elif prefix in prefixes:
        errors.append(f"{rel}: id_prefix {prefix} already used by {prefixes[prefix]}")
    else:
        prefixes[prefix] = rel

    _, body = split_front_matter(text)
    headings = [(len(match.group(1)), match.group(2).strip()) for match in _HEADING.finditer(body)]
    h1 = [title for level, title in headings if level == 1]
    h2 = [title for level, title in headings if level == 2]
    h3 = [title for level, title in headings if level == 3]
    if h1 != ["测试用例"]:
        errors.append(f"{rel}: H1 must be exactly 测试用例")
    if h2 != [module_name]:
        errors.append(f"{rel}: H2 must be exactly {module_name}")
    if h3 != [path.stem]:
        errors.append(f"{rel}: H3 must be exactly {path.stem}")

    lines = body.splitlines()
    case_starts = [index for index, line in enumerate(lines) if line.startswith("#### ")]
    for offset, start in enumerate(case_starts):
        end = case_starts[offset + 1] if offset + 1 < len(case_starts) else len(lines)
        heading = lines[start]
        matched = CASE_HEADING.match(heading)
        if not matched:
            errors.append(
                f"{rel}: case heading must be '#### User-Login0001 正向-|反向-<name>' ({heading})"
            )
            continue
        case_prefix, seq = matched.group(1), matched.group(2)
        case_id = f"{case_prefix}{seq}"
        if prefix and case_prefix != prefix:
            errors.append(f"{rel}: {case_id} must use id_prefix {prefix}")
        previous = seen.get(case_id)
        if previous:
            errors.append(f"{rel}: duplicate {case_id} (also in {previous})")
        else:
            seen[case_id] = rel
        block = lines[start + 1 : end]
        if not any(STEP_BULLET.match(line) for line in block):
            errors.append(f"{rel}: {case_id} needs '- 步骤：'")
        if not any(EXPECT_BULLET.match(line) for line in block):
            errors.append(f"{rel}: {case_id} needs '- 预期：'")
    return errors


def _check_kind(path: Path, kind: str) -> list[str]:
    meta = parse_front_matter(path.read_text(encoding="utf-8"))
    if meta.get("kind") != kind:
        return [f"{_rel(path)}: front-matter kind must be {kind}"]
    return []


def _rel(path: Path) -> str:
    return path.as_posix()
