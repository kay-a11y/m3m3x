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

# === base2img ===
def read_path(filepath: str) -> List[Path]:
    """Given a path, return list of file Paths."""
    filepath = Path(filepath)

    if filepath.is_dir():
        click.secho("Handle as folder", fg="cyan")
        files: List[Path] = []
        for file in filepath.iterdir():
            click.secho(f"file={file}", fg="cyan", bold=True)
            files.append(file)
        return files
    elif filepath.is_file():
        click.secho("Handle as file", fg="cyan")
        return [filepath]
    else:
        click.secho("[!] Not found, or special type", fg="red", bold=True)
        return  []
    
def read_file(files: List[Path]) -> list[str]:
    """Given list of file Paths, return their contents as strings."""
    file_strs: List[str] = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            file_strs.append(content)
    return file_strs

def read_basename(files: List[Path]) -> List[str]:
    """Given list of file Paths, return list of their basename (without ext)"""
    return [file.stem for file in files]
    # basenames: List[str] = []
    # for file in files:
    #     basenames.append(file.stem)
    # return basenames

__all__ = ["read_lines", "write_lines"]
