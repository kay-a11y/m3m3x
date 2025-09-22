#!/usr/bin/env python3
"""
memex.cli  - Top-level command group
====================================

Entrypoint wired in *pyproject.toml*:

```toml
[project.scripts]
memex = "memex.cli:cli"
````

Provides a single Click *Group* named `cli` which aggregates all
sub-commands found in `memex.scripts`.

Adding a new command
-----
1. Create `memex/scripts/<verb>.py` with a `@click.command`.

2. Import and register it here:

   ```python
   from memex.scripts.links import links_cmd
   cli.add_command(links_cmd)
   ```

3. Re-install in editable mode or just `pip install -e .` once.
"""

import click
from memex.scripts.clean import clean_cmd
from memex.scripts.init import init_cmd
from memex.scripts.new import new_cmd
from memex.scripts.base2img import base2img_cmd
from memex.scripts.yfm import yfm_cmd

@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=False,
    help="Memex CLI. Run `memex <command> -h` for details.",
)
def cli() -> None:
    pass

cli.add_command(clean_cmd)
cli.add_command(init_cmd)
cli.add_command(new_cmd)
cli.add_command(base2img_cmd)
cli.add_command(yfm_cmd)

if __name__ == "__main__":
    cli()
