"""
memex new - Create a new Markdown doc with YAML front matter
===========================================================

Usage
-----
```bash
memex new <slug> [--interactive | --folder NAME | --cats JSON --tags JSON]
````

Description
-----
Scaffolds a new Markdown file in `docs/<folder>/` with
auto-generated front matter (title from filename, dates, defaults).
Interactive mode prompts for folder → categories → tags.

Options
-----
--interactive     Prompt for folder, categories, and tags.
--folder NAME     Skip folder prompt, place file directly under NAME.
--cats JSON       Explicit categories (overrides defaults/prompts).
--tags JSON       Explicit tags (overrides defaults/prompts).
"""