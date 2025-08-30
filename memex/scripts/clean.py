#!/usr/bin/env python3
"""
memex clean  - Normalize Unicode punctuation in Markdown files
==============================================================

CLI sub-command registered under the top-level `memex` executable.

Usage
-----
```bash
# Print cleaned text to STDOUT
memex clean README.md

# Overwrite files in place
memex clean docs/**/*.md -w
```

Arguments
--------
`files`  
    One or more file paths (globs work when shell-expanded).

Options  
--------  
-w, --write   Overwrite each file in place (default is to print).
"""

from pathlib import Path

import click

from memex.utils import read_lines, resolve_pathish, write_lines
from memex.utils.text import clean_punctuation


@click.command("clean")
@click.argument("files", nargs=-1, type=str, required=True)
@click.option("-w", "--write", is_flag=True, 
              help="Overwrite the file(s) instead of printing.")
def clean_cmd(files: tuple[str], write: bool) -> None:
    """Clean one or many FILES."""
    for raw in files:
        path: Path = resolve_pathish(raw)

        text = "".join(read_lines(path, missing_ok=False))
        fixed = clean_punctuation(text)

        if write:
            write_lines(path, [fixed])
            click.secho(f"🖊️ scrubbed {path}", fg="green")
        else:
            click.echo(fixed)
