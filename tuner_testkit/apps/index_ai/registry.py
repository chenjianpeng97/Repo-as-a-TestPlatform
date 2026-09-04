"""Scan ``.cursor/**`` AI components and render ``.cursor/REGISTRY.md``.

Deterministic (no LLM): parses lightweight front-matter from rules/skills/agents
and the ``.cursor/hooks.json`` event map, then renders a Markdown registry. Also
supports ``--check`` (used by CI / a sync hook) to detect drift.
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, field

from tuner_testkit.project import project_root

_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")


def _repo_root() -> pathlib.Path:
    return project_root()


def _cursor_dir() -> pathlib.Path:
    return _repo_root() / ".cursor"


def _registry_path() -> pathlib.Path:
    return _cursor_dir() / "REGISTRY.md"


@dataclass
class Component:
    kind: str            # rule | skill | agent | hook
    name: str
    trigger: str
    scope: str
    description: str
    version: str
    path: str
    extra: dict = field(default_factory=dict)


def parse_front_matter(text: str) -> dict[str, str]:
    """Minimal YAML-ish front-matter parser (delimited by ``---``).

    Handles ``key: value`` and folded/literal blocks (``>-`` / ``|``). No third
    party deps; good enough for this repo's simple front-matter.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}

    fm: dict[str, str] = {}
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = _KEY_RE.match(line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-"):
            block: list[str] = []
            i += 1
            while i < end and (lines[i].startswith(("  ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            sep = " " if val.startswith(">") else "\n"
            fm[key] = sep.join(b for b in block if b)
            continue
        fm[key] = val
        i += 1
    return fm


def _first_sentence(text: str, limit: int = 120) -> str:
    text = " ".join(text.split())
    if not text:
        return "-"
    # Cut at a sentence end: CJK 。；, or ./; only when followed by whitespace
    # (so file extensions like ".feature" are not treated as sentence ends).
    m = re.search(r"[。；]|[.;](?=\s)", text)
    cut = text[: m.start()] if m else text
    if len(cut) > limit:
        cut = cut[: limit - 1] + "…"
    return cut or "-"


def collect_rules() -> list[Component]:
    out: list[Component] = []
    for path in sorted((_cursor_dir() / "rules").glob("*.mdc")):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        always = str(fm.get("alwaysApply", "")).strip().lower() == "true"
        globs = fm.get("globs", "").strip()
        if always:
            trigger, scope = "always", "all files"
        elif globs:
            trigger, scope = "glob", globs
        else:
            trigger, scope = "manual", "-"
        out.append(Component(
            kind="rule",
            name=path.stem,
            trigger=trigger,
            scope=scope,
            description=_first_sentence(fm.get("description", "")),
            version=fm.get("version", "-").strip() or "-",
            path=str(path.relative_to(_repo_root())).replace("\\", "/"),
        ))
    return out


def _collect_named(subdir: str, pattern: str, kind: str, trigger: str) -> list[Component]:
    out: list[Component] = []
    for path in sorted((_cursor_dir() / subdir).glob(pattern)):
        fm = parse_front_matter(path.read_text(encoding="utf-8"))
        out.append(Component(
            kind=kind,
            name=fm.get("name", path.parent.name if path.name == "SKILL.md" else path.stem),
            trigger=trigger,
            scope="-",
            description=_first_sentence(fm.get("description", "")),
            version=fm.get("version", "-").strip() or "-",
            path=str(path.relative_to(_repo_root())).replace("\\", "/"),
        ))
    return out


def collect_skills() -> list[Component]:
    return _collect_named("skills", "*/SKILL.md", "skill", "on-demand")


def collect_agents() -> list[Component]:
    return _collect_named("agents", "*.md", "agent", "orchestration")


def collect_hooks() -> list[Component]:
    out: list[Component] = []
    hooks_json = _cursor_dir() / "hooks.json"
    if hooks_json.exists():
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        for event, entries in (data.get("hooks") or {}).items():
            for entry in entries:
                cmd = entry.get("command", entry.get("type", "prompt"))
                out.append(Component(
                    kind="hook",
                    name=f"{event}",
                    trigger=event,
                    scope=entry.get("matcher", "-") or "-",
                    description=f"command: {cmd}",
                    version=str(data.get("version", "-")),
                    path=".cursor/hooks.json",
                ))
    # git hooks (not agent hooks) — listed for completeness
    git_hooks = _repo_root() / "tools" / "git-hooks"
    if (git_hooks / "commit-msg").exists():
        out.append(Component(
            kind="hook",
            name="commit-msg",
            trigger="git commit",
            scope="tools/git-hooks",
            description="Conventional Commits + layer-scope consistency check",
            version="-",
            path="tools/git-hooks/commit-msg",
        ))
    return out


def _render_table(title: str, comps: list[Component]) -> str:
    lines = [f"## {title}", ""]
    if not comps:
        lines.append("_(暂无)_")
        lines.append("")
        return "\n".join(lines)
    lines.append("| 名称 | 触发 | 作用范围 | 版本 | 职责 | 文件 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for c in comps:
        scope = c.scope.replace("|", "\\|")
        desc = c.description.replace("|", "\\|")
        lines.append(
            f"| `{c.name}` | {c.trigger} | {scope} | {c.version} | {desc} | `{c.path}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render() -> str:
    rules = collect_rules()
    skills = collect_skills()
    agents = collect_agents()
    hooks = collect_hooks()
    total = len(rules) + len(skills) + len(agents) + len(hooks)

    header = (
        "<!-- GENERATED by `python -m tuner_testkit.apps.index_ai`. Do not edit by hand. -->\n"
        "# REGISTRY — AI 组件注册表（平台后端服务）\n"
        "\n"
        "> `.cursor/**` 下的 rule / skill / agent / hook 相当于测试平台后端 service 的\n"
        "> 业务规则与处理逻辑。本表由 `python -m tuner_testkit.apps.index_ai` 扫描各组件 front-matter\n"
        "> 确定性生成，供人类工程师一眼看全当前能力与版本。稳定世界观见 `AGENTS.md`；\n"
        "> 知识/能力地图见 `INDEX.md`。\n"
        "\n"
        f"> 组件总数：**{total}**（rules {len(rules)} · skills {len(skills)} · "
        f"agents {len(agents)} · hooks {len(hooks)}）\n"
    )
    body = "\n".join([
        "",
        _render_table("Rules（约束/边界）", rules),
        _render_table("Skills（操作流程）", skills),
        _render_table("Agents（编排 playbook）", agents),
        _render_table("Hooks（事件驱动脚本）", hooks),
    ])
    return header + body


def write() -> pathlib.Path:
    _registry_path().write_text(render(), encoding="utf-8", newline="\n")
    return _registry_path()


def is_current() -> bool:
    if not _registry_path().exists():
        return False
    return _registry_path().read_text(encoding="utf-8") == render()
