# m3m3x

m3m3x is my chaotic little **`memex`**, a personal knowledge vault wired up with auto generated YAML front matter, CLI helpers, and a flexible docs structure.  

## Quick‑start

```bash
git clone https://github.com/kay-a11y/m3m3x.git
cd m3m3x

pip install -e .

# Check available commands
memex --help

# Example: scrub weird Unicode quotes in place
memex clean docs/git/*.md -w

# Initialize config file
memex init

# drop a new post with auto generated YAML front matter
memex new git-cheatsheet --interactive
```

## Usage

```txt
Usage: memex [OPTIONS] COMMAND [ARGS]...

  Memex CLI. Run `memex <command> -h` for details.

Options:
  -h, --help  Show this message and exit.

Commands:
  clean  Clean one or many FILES.
  init   Initialize .memex.yml and docs/_data/taxonomy.yml.
  new    Create docs/<folder>/YYYY-MM-DD-<slug>.md with front matter from...
```