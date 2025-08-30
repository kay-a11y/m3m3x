#!/usr/bin/env python3
"""
memex init - Initialize `.memex.yml` and `docs/_data/taxonomy.yml`
=================================================================

Usage
-----
```bash
memex init [--force]
````

Description
-----
Create the default configuration files for memex:

* `.memex.yml` at the repo root (tool defaults, dir rules, acronym map)
* `docs/_data/taxonomy.yml` (categories & tags for prompts and Jekyll)

Options
-----
--force       Overwrite existing config files if they already exist.
"""

from pathlib import Path

import click
import yaml

from memex.utils import REPO_ROOT, resolve_pathish

DEFAULT_MEMEX_YML = """\
timezone: "Africa/Abidjan"
frontmatter_defaults:
  layout: "post"  # defaults to "post"
  img_path: "/assets/img/posts/"
  math: true
  toc: true
  comments: true
  image: ""  # the cover, defaults to blank
titlecase:
  acronym_map:
    nmap: "Nmap"
    cli: "CLI"
    lan: "LAN"
    llm: "LLM"
    iot: "IoT"
    wifi: "Wi-Fi"
yfm:
  enforce_key_order:
    - layout
    - title
    - description
    - date
    - last_update
    - categories
    - tags
    - img_path
    - math
    - toc
    - comments
    - image
dir_rules:
  "docs/aws/**":
    categories: ["🤖 tech","✈️ aws"]
  "docs/cheatsheets/**":
    categories: ["🤖 tech","📖 cheatsheet"]
  "docs/drafts/**":
    categories: ["📝 drafts"]
  "docs/git/**":
    categories: ["🤖 tech","🧙 git"]
  "docs/homenet/**":
    categories: ["🤖 tech","🏠 homenet"]
  "docs/learning_routes/**":
    categories: ["🤖 tech","📚 learning_routes"]
  "docs/linux/**":
    categories: ["🤖 tech","🐧 linux"]
  "docs/LLM/**":
    categories: ["🤖 tech","🤖 LLM"]
  "docs/opsec/**":
    categories: ["🤖 tech","💳 opsec"]
  "docs/proxy/**":
    categories: ["🤖 tech","✈️ proxy"]
"""

DEFAULT_TAXONOMY_YML = """\
categories:
  "🤖 tech": "🤖 tech"
  "✈️ aws": "✈️ aws"
  "📖 cheatsheet": "📖 cheatsheet"
  "📝 drafts": "📝 drafts"
  "🧙 git": "🧙 git"
  "🏠 homenet": "🏠 homenet"
  "🐧 linux": "🐧 linux"
  "🤖 LLM": "🤖 LLM"
  "💳 opsec": "💳 opsec"
  "✈️ proxy": "✈️ proxy"

tags:
  "🐧 Linux": "🐧 Linux"
  "🖥️ CLI": "🖥️ CLI"
  "🛜 IoT": "🛜 IoT"
  "🔀 LAN": "🔀 LAN"
  "🧙🏻 Git": "🧙🏻 Git"
  "🕵🏻️ Nmap": "🕵🏻️ Nmap"
  "📷 Cam": "📷 Cam"
  "🔒 Privacy": "🔒 Privacy"
"""

@click.command("init")
@click.option("--force", is_flag=True, 
              help="Overwrite existing config files.")
def init_cmd(force: bool):
    """Initialize .memex.yml and docs/_data/taxonomy.yml."""
    memex_yml = REPO_ROOT / ".memex.yml"
    taxonomy_yml = resolve_pathish("docs/_data/taxonomy.yml")

    if not memex_yml.exists() or force:
        memex_yml.write_text(DEFAULT_MEMEX_YML)
        click.echo(f"✔ Wrote {memex_yml}")
    else:
        click.echo(f"! Skipped {memex_yml} , already exists.")

    taxonomy_yml.parent.mkdir(parents=True, exist_ok=True)
    if not taxonomy_yml.exists() or force:
        taxonomy_yml.write_text(DEFAULT_TAXONOMY_YML)
        click.echo(f"✔ Wrote {taxonomy_yml}")
    else:
        click.echo(f"! Skipped {taxonomy_yml} , already exists.")
