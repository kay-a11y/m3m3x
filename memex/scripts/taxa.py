"""
memex taxa – manage categories and tags
=======================================

Usage
-----
```bash
memex taxa list <cats|tags>
memex taxa add  <cats|tags> "<value1>" ["<value2>" ...]
memex taxa rm   <cats|tags> "<value1>" ["<value2>" ...]
````

Description
-----------
Work with your memex taxonomy (categories and tags).

* `list`: show all current categories or tags.
* `add`:  add one or more new categories/tags.
* `rm`:   remove one or more categories/tags.

Arguments
---------

<cats|tags>   choose whether to manage categories (`cats`) or tags (`tags`) 
<value>       one or more values to add/remove; wrap each in quotes if needed

Examples
--------
# List categories
memex taxa list cats

# List tags
memex taxa list tags

# Add a category "proj" and "life"
memex taxa add cats "proj" "life"

# Add tags "idea" and "hack"
memex taxa add tags "idea" "hack"

# Remove category "proj"
memex taxa rm cats "proj"

# Remove tags "idea" and "hack"
memex taxa rm tags "idea" "hack"
"""

from __future__ import annotations

from typing import Tuple, List

import click

from memex.utils import resolve_pathish
from memex.utils.load import load_yaml

from memex.utils.symbols import CHECK, WARN
from memex.utils.yaml_tools import dump_no_wrap


TAXONOMY_YML = resolve_pathish("docs/_data/taxonomy.yml")

def _load_taxonomy() -> dict[str, dict[str, str]]:
    """Load the taxonomy file fresh each time."""
    return load_yaml(TAXONOMY_YML)

def _save_taxonomy(content: dict) -> None:
    """Dump taxonomy content back to YAML file."""
    TAXONOMY_YML.write_text(dump_no_wrap(content), encoding="utf-8")

def _update_taxonomy(kind: str, action: str, values: Tuple[str, ...]) -> tuple[List[str], List[str]]:
    """
    Update taxonomy (categories/tags).

    Args:
        kind: "cats" or "tags"
        action: "add" or "rm"
        values: values to process

    Returns:
        (changed, skipped) where:
          - changed = values successfully added/removed
          - skipped = values not found or unchanged
    """
    taxonomy_content = _load_taxonomy()
    section = "categories" if kind == "cats" else "tags"
    section_dict = taxonomy_content.setdefault(section, {})

    changed, skipped = [], []

    for value in values:
        if action == "add":
            if value not in section_dict:
                section_dict[value] = value
                changed.append(value)
            else:
                skipped.append(value)
        elif action == "rm":
            if section_dict.pop(value, None) is not None:
                changed.append(value)
            else:
                skipped.append(value)

    _save_taxonomy(taxonomy_content)
    return changed, skipped


@click.group("taxa")
def taxa_cmd():
    """
    Work with your memex taxonomy (categories and tags).

    * `list`: show all current categories or tags.

    * `add`:  add one or more new categories/tags.

    * `rm`:   remove one or more categories/tags.
    """
    pass


# === Click command ===
@taxa_cmd.command("list")
@click.argument("kind", type=click.Choice(["cats", "tags"]))
def list_cmd(kind: str) -> None:
    """
    Show all current categories or tags.
    """

    taxonomy_content = load_yaml(TAXONOMY_YML)
    section = "categories" if kind == "cats" else "tags"
    print(*[f"{k}: {v}" for k, v in taxonomy_content.get(section, {}).items()], sep="\n")


@taxa_cmd.command("add")
@click.argument("kind", type=click.Choice(["cats", "tags"]))
@click.argument("values", nargs=-1)
def add_cmd(kind: str, values: Tuple[str, ...]) -> None:
    """Add one or more new categories/tags."""
    if not values:
        raise click.ClickException("No value given. Pass value(s) for cats/tags")

    added, skipped = _update_taxonomy(kind, "add", values)

    if added:
        click.secho(f"{CHECK} Added {', '.join(added)} to {kind}", fg="green")
    if skipped:
        click.secho(f"{WARN} Already present: {', '.join(skipped)} in {kind}", fg="yellow")


@taxa_cmd.command("rm")
@click.argument("kind", type=click.Choice(["cats", "tags"]))
@click.argument("values", nargs=-1)
def rm_cmd(kind: str, values: Tuple[str, ...]) -> None:
    """Remove one or more categories/tags."""
    if not values:
        raise click.ClickException("No value given. Pass value(s) for cats/tags")

    removed, missing = _update_taxonomy(kind, "rm", values)

    if removed:
        click.secho(f"{CHECK} Removed {', '.join(removed)} from {kind}", fg="green")
    if missing:
        click.secho(f"{WARN} Not found: {', '.join(missing)} in {kind}", fg="yellow")
