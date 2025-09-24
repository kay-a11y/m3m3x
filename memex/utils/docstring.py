"""
memex new - Create a new Markdown doc with YAML front matter
===========================================================

Usage
-----
```bash
memex new <slug> [--interactive | --folder NAME | --cats JSON --tags JSON]
````

Description
-----------
Scaffolds a new Markdown file in `docs/<folder>/` with
auto-generated front matter (title from filename, dates, defaults).
Interactive mode prompts for folder → categories → tags.

Arguments
---------

<cats|tags>   choose whether to manage categories (`cats`) or tags (`tags`) 
<value>       one or more values to add/remove; wrap each in quotes if needed

Options
-------
--interactive     Prompt for folder, categories, and tags.
--folder NAME     Skip folder prompt, place file directly under NAME.
--cats JSON       Explicit categories (overrides defaults/prompts).
--tags JSON       Explicit tags (overrides defaults/prompts).

Examples - memex yfm touch
--------
# Update a single file
memex yfm touch docs/homenet/2025-08-10-netmap.md

# Update multiple files
memex yfm touch docs/linux/*.md

# Be explicit with the flag (same result)
memex yfm touch docs/linux/*.md --last-update
"""
