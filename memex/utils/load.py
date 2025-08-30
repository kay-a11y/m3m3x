"""
Lightweight text file helpers with repo-root resolution.

Accepts either:
- POSIX-like relative strings: "docs/git/2025-07-18-git-privacy.md"
- pathlib.Path objects (absolute or relative)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional, Union

import click
import yaml

from memex.utils.path import resolve_pathish

Pathish = Union[str, Path]

def read_lines(pathish: Pathish, missing_ok: bool = True, encoding: str = "utf-8") -> List[str]:
    """
    Return list of lines. If file missing and missing_ok, return [].
    """
    p = resolve_pathish(pathish)
    try:
        with p.open("r", encoding=encoding) as f:
            return f.readlines()
    except FileNotFoundError:
        if missing_ok:
            return []
        raise

def write_lines(pathish: Pathish, lines: Iterable[str], encoding: str = "utf-8") -> None:
    """
    Write iterable of lines to file, creating parent dirs if needed.
    """
    p = resolve_pathish(pathish)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding) as f:
        for ln in lines:
            f.write(ln)

# === YAML ===
def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        click.secho(f"✘ Failed to parse {path}: {e}", fg="red")
        return {}

# === JSON ===
def safe_json_array(s: Optional[str]) -> Optional[List[str]]:
    if not s:
        return None
    try:
        arr = json.loads(s)
        if isinstance(arr, list) and all(isinstance(x, str) for x in arr):
            return arr
    except Exception:
        pass
    raise click.BadParameter('Expected JSON array of strings, e.g. \'["🤖 tech","🐧 linux"]\'')


__all__ = ["read_lines", "write_lines"]
