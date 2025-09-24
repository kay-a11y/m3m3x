"""
memex yfm - Detect front matter, insert/update, normalize key order/quotes.
memex yfm touch - Update YAML front matter fields
===========================================================

Usage
-----
```bash
memex yfm ensure <PATH...> [--interactive --explain]
memex yfm fmt <PATH...>
memex yfm lint <PATH...>
memex yfm touch <PATH...> [--last-update]
```

Description
-----------
yfm ensure/fmt/lint/touch commands.

Options
-------
--interactive     Prompt for folder, categories, and tags.
--last-update     Prompt for yaml part.

Examples - memex yfm touch
--------
    # Update a single file
    memex yfm touch docs/homenet/2025-08-10-netmap.md

    # Update multiple files
    memex yfm touch docs/linux/*.md

    # Be explicit with the flag (same result)
    memex yfm touch docs/linux/*.md --last-update
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import click
import yaml

from memex.utils.date import now_str
from memex.utils.symbols import CHECK, FAIL
from memex.utils.yaml_tools import FlowList, MemexDumper


@click.group("yfm")
def yfm_cmd():
    """YAML Front Matter helpers (inspect, edit, touch)."""
    pass


# === Click command ===
@yfm_cmd.command("touch")
@click.argument("paths", nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--last-update", "do_last_update", is_flag=True, default=True,
              help="Update the 'last_update' field (default).")
def touch_cmd(paths: List[Path], do_last_update: bool) -> None:
    """
    Update YAML front matter in the given file(s).

    PATH... : One or more markdown files to update.
    """
    if not paths:
        raise click.ClickException("No files given. Pass one or more markdown files.")

    for path in paths:
        text = path.read_text(encoding="utf-8")

        # Split YFM from body
        if not text.startswith("---"):
            click.echo(f"{FAIL} {path}: no YAML front matter found")
            continue

        try:
            _, fm_text, body = text.split("---", 2)
        except ValueError:
            click.echo(f"{FAIL} {path}: malformed YAML front matter")
            continue

        fm = yaml.safe_load(fm_text) or {}

        # ensure flow style for categories & tags
        if "categories" in fm and isinstance(fm["categories"], list):
            fm["categories"] = FlowList(fm["categories"])
        if "tags" in fm and isinstance(fm["tags"], list):
            fm["tags"] = FlowList(fm["tags"])

        # Update field(s)
        if do_last_update:
            fm["last_update"] = now_str()

        # Reconstruct file
        new_front = yaml.dump(fm, 
                               Dumper=MemexDumper,
                               sort_keys=False, 
                               allow_unicode=True, 
                               default_flow_style=False # block mapping overall; flow only for FlowList
                               ).strip()
        new_text = f"---\n{new_front}\n---{body}"
        path.write_text(new_text, encoding="utf-8")

        click.echo(f"{CHECK} touched {path}")
