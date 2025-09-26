# m3m3x

m3m3x is my chaotic little **`memex`**, a personal knowledge vault wired up with auto generated YAML front matter, CLI helpers, and a flexible docs structure.  

[Read the full Wiki →](https://github.com/kay-a11y/m3m3x/wiki)

## Setup

```bash
git clone https://github.com/kay-a11y/m3m3x.git
cd m3m3x
pip install -e .
memex --help
```

##  Core commands

```bash
# Initialize config + taxonomy files
memex init

# Drop a new post with auto generated YAML front matter
memex new git-cheatsheet --interactive

# Update the `last_update` field in a file
memex yfm touch docs/homenet/2025-08-10-netmap.md
```

## Cleaning & utilities

```bash
# Scrub weird Unicode quotes in place
memex clean docs/git/*.md -w

# Decode base64 images in Markdown and rewrite links
memex base2img docs/drafts/example.md
```

## Taxonomy (categories & tags)

```bash
# List categories / tags
memex taxa list cats
memex taxa list tags

# Add new categories / tags
memex taxa add cats "proj" "life"
memex taxa add tags "idea" "hack"

# Remove categories / tags
memex taxa rm cats "proj"
memex taxa rm tags "idea" "hack"
```

## Cheat Sheet

```bash
Usage: memex [OPTIONS] COMMAND [ARGS]...

  Memex CLI. Run `memex <command> -h` for details.

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  base2img  Decode base64 images in Markdown and rewrite links to saved files.
  clean     Normalize Unicode punctuation in Markdown files for one or many FILES.
  init      Initialize .memex.yml and docs/_data/taxonomy.yml.
  new       Create docs/<folder>/YYYY-MM-DD-<slug>.md with front matter from configs.
  taxa      Work with your memex taxonomy (categories and tags).
  yfm       YAML Front Matter helpers (inspect, edit, touch).
```
