"""
memex new - Create a new Markdown doc with YAML front matter
===========================================================

Usage
-----
```bash
memex new <slug> [--interactive | --folder NAME | --cats JSON --tags JSON]
```

Description
-----------
Scaffolds a new Markdown file in `docs/<folder>/` with auto-generated
front matter (title from slug, dates, defaults from `.memex.yml`).
Interactive mode prompts for folder → categories → tags pulled from
`docs/_data/taxonomy.yml`.

Options
-------
--interactive     Prompt for folder, categories, and tags.
--folder NAME     Skip folder prompt; place file under NAME (must exist in docs/).
--cats JSON       Explicit categories (JSON array) overrides rules/prompts.
--tags JSON       Explicit tags (JSON array) overrides rules/prompts.
"""

from __future__ import annotations

import json
import re
from logging import getLogger
from pathlib import Path
from typing import Iterable, List, Optional

import click
import yaml

from memex.utils import REPO_ROOT, log_call, resolve_pathish
from memex.utils.date import now_str, today_iso
from memex.utils.load import load_yaml, safe_json_array
from memex.utils.symbols import ARROW, CHECK, FAIL, WARN
from memex.utils.title import title_from_filename
from memex.utils.yaml_tools import FlowList, MemexDumper

log = getLogger("memex")

# === Small utils ===
def _dedup_preserving_order(items: list[str]) -> List[str]:
    """a de-dup util"""
    seen = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _sanitize_slug(slug: str) -> str:
    """
    Strip a trailing '.md' and any leading 'YYYY-MM-DD-' date prefix.
    """
    s = slug.strip()
    if s.lower().endswith(".md"):
        s = s[:-3]
    s = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", s)
    return s
 
# === Folder / rules helpers ===
def _list_docs_subfolders(docs_dir: Path) -> List[str]:
    """
    return list of parent folders of the doc as categories 
    """
    if not docs_dir.exists():
        return []
    return sorted([p.name for p in docs_dir.iterdir() if p.is_dir()])


def _infer_categories_for_folder(folder: str, dir_rules: dict) -> List[str]:
    """
    dir_rules keys look like 'docs/cheatsheets/**' -> categories: [...]
    We match by checking if the pattern startswith 'docs/<folder>/'.
    """
    # match `dir_rules` in `.memex.yml`, then make them as cats
    want_prefix = f"docs/{folder}/"
    inferred: List[str] = []
    for pattern, rule in (dir_rules or {}).items():
        if isinstance(rule, dict) and "categories" in rule:
            if str(pattern).startswith(want_prefix):
                cats = rule.get("categories") or []
                if isinstance(cats, list):
                    inferred.extend(cats)
    # de-dup preserving order
    return _dedup_preserving_order(inferred)


# === Simple interactive prompts (numbered select) ===
def _cli_single_select(title: str, options: List[str], preselect: Optional[str] = None) -> Optional[str]:
    """Simple *single-choice* prompt by number. Returns chosen value or None."""
    click.echo(f"{ARROW} {title}")
    if not options:
        click.echo(f"{WARN} No options available.")
        return None
    index_map = {i + 1: v for i, v in enumerate(options)}
    default_idx = None
    if preselect and preselect in options:
        default_idx = options.index(preselect) + 1
    for i, v in index_map.items():
        mark = "•" if (default_idx == i) else " "
        click.echo(f"  {i:>2}) {mark} {v}")
    raw = click.prompt("Choose one by number", default=str(default_idx) if default_idx else "", show_default=False)
    if not raw.strip():
        return preselect if preselect in options else None
    try:
        idx = int(raw.strip())
    except ValueError:
        click.echo(f"{WARN} Invalid selection; using default.")
        return preselect if preselect in options else None
    return index_map.get(idx, preselect if preselect in options else None)


def _cli_multiselect(title: str, options: List[str], prechecked: Optional[Iterable[str]] = None) -> List[str]:
    """
    Numbered multi-select. User types comma-separated indices.
    Example:
      1) 🧙🏻 Git
      2) 🐧 Linux
    Input: 1,2
    """
    click.echo(f"{ARROW} {title}")
    if not options:
        click.echo(f"{WARN} No options available.")
        return []
    index_map = {i + 1: v for i, v in enumerate(options)}
    pre = set(prechecked or [])

    # make serial numbers right-aligned
    for i, v in index_map.items():
        mark = "[x]" if v in pre else "[ ]"
        click.echo(f"  {i:>2}) {mark} {v}")

    raw = click.prompt("Select by number (comma-separated), or blank for none", default="", show_default=False)
    if not raw.strip():
        return list(pre) if pre else []
    
    sel: List[str] = []
    for chunk in re.split(r"[,\s]+", raw.strip()):
        if not chunk:
            continue
        try:
            idx = int(chunk)
        except ValueError:
            click.echo(f"{WARN} Ignored invalid token: {chunk}")
            continue
        if idx in index_map:
            sel.append(index_map[idx])
        else:
            click.echo(f"{WARN} Out-of-range index: {idx}")
    # de-dup preserving order
    return _dedup_preserving_order(sel)


# === Click command ===
@click.command("new")
@click.argument("slug", nargs=1)
@click.option("--interactive", is_flag=True, 
              help="Prompt for folder, categories, and tags.")
@click.option("--folder", type=str, default=None, 
              help="Target folder under docs/ (e.g., cheatsheets, linux).")
@click.option("--cats", type=str, default=None, 
              help='Explicit categories as JSON array, overrides prompts/rules.')
@click.option("--tags", type=str, default=None, 
              help='Explicit tags as JSON array, overrides prompts/rules.')
@click.option("--force", is_flag=True, 
              help="Overwrite if file exists (makes a .bak by default).")
@click.option("--no-backup", is_flag=True, 
              help="When used with --force, do not create a backup.")
def new_cmd(slug: str, interactive: bool, folder: Optional[str], cats: Optional[str], tags: Optional[str], force: bool, no_backup: bool) -> None:
    """
    Create docs/<folder>/YYYY-MM-DD-<slug>.md with front matter from configs.
    """
    docs_dir = resolve_pathish("docs")
    exclude_folder = {"_data", "assets"}
    memex_yml = resolve_pathish(".memex.yml")
    taxonomy_yml = resolve_pathish("docs/_data/taxonomy.yml")

    cfg = load_yaml(memex_yml)
    taxonomy = load_yaml(taxonomy_yml)

    fm_defaults = cfg.get("frontmatter_defaults") or {}
    dir_rules = cfg.get("dir_rules") or {}
    titlecase = (cfg.get("titlecase") or {})
    acronym_map = titlecase.get("acronym_map", {}) or {}
    lil_words = titlecase.get("lil_words", []) or []

    # 1) Choose folder
    folders = [f for f in _list_docs_subfolders(docs_dir) if f not in exclude_folder]
    if interactive and not folder:
        preselect = folders[0] if folders else None
        folder = _cli_single_select("Select folder", folders, preselect=preselect)
    if not folder:
        raise click.ClickException("Missing folder. Use --interactive or specify --folder NAME.")
    if folder not in folders:
        raise click.ClickException(f"Folder '{folder}' not found under docs/. Existing: {', '.join(folders) or '(none)'}")

    # 2) Compute path & times
    base_slug = _sanitize_slug(slug)
    md_name = f"{today_iso()}-{base_slug}.md"
    out_dir = docs_dir / folder
    out_path = out_dir / md_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # 3) Title
    title = title_from_filename(base_slug, acronym_map, lil_words)

    # 4) Categories/Tags
    explicit_cats = safe_json_array(cats)
    explicit_tags = safe_json_array(tags)

    inferred_cats = _infer_categories_for_folder(folder, dir_rules)
    avail_cats = list((taxonomy.get("categories") or {}).keys())
    avail_tags = list((taxonomy.get("tags") or {}).keys())

    if interactive:
        picked_cats = _cli_multiselect("Select categories", avail_cats, inferred_cats)
        picked_tags = _cli_multiselect("Select tags", avail_tags, [])
    else:
        picked_cats = inferred_cats
        picked_tags = []

    final_categories = explicit_cats if explicit_cats is not None else picked_cats
    final_tags = explicit_tags if explicit_tags is not None else picked_tags

    # 5) Build front matter
    fm = {
         "layout": fm_defaults.get("layout", "post"),
         "title": title,
         "description": "",
         "date": now_str(),
         "last_update": now_str(),
        "categories": FlowList(final_categories or []),
        "tags": FlowList(final_tags or []),
         "img_path": fm_defaults.get("img_path", "/assets/img/posts/"),
         "math": bool(fm_defaults.get("math", True)),
         "toc": bool(fm_defaults.get("toc", True)),
         "comments": bool(fm_defaults.get("comments", True)),
         "image": fm_defaults.get("image", ""),
     }
    
    # 6) Write (with safe overwrite)
    if out_path.exists():
        if not force:
            raise click.ClickException(f"{FAIL} File already exists: {out_path}. Use --force to overwrite.")
        # make a backup unless explicitly disabled
        if not no_backup:
            from datetime import datetime
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = out_path.with_suffix(out_path.suffix + f".bak.{stamp}")
            backup.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
            click.echo(f"{WARN} Backup written: {backup.relative_to(REPO_ROOT)}")

    front = yaml.dump(fm, 
                           Dumper=MemexDumper,
                           sort_keys=False, 
                           allow_unicode=True, 
                           default_flow_style=False # block mapping overall; flow only for FlowList
                           ).strip()
    

    content = f"---\n{front}\n---\n\n"
    out_path.write_text(content, encoding="utf-8")

    # 7) Echo result
    rel_path = out_path.relative_to(REPO_ROOT)
    click.echo(f"{CHECK} Created {rel_path}")
    click.echo(f"{ARROW} title: {title}")
    click.echo(f"{ARROW} categories: {final_categories or '[]'}")
    click.echo(f"{ARROW} tags: {final_tags or '[]'}")
