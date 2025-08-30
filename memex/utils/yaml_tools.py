"""
memex.utils.yaml_tools - YAML helpers for pretty front matter
"""

import yaml


def dump_no_wrap(data: dict) -> str:
    """
    Dump YAML without automatic line-wrapping so long scalars stay intact.
    """
    return yaml.dump(
        data,
        sort_keys=False,
        width=10**9,
        allow_unicode=True,
    )


class FlowList(list):
    """List that always dumps in YAML flow style: [a, b, c]."""
    pass

def _represent_flow_seq(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)

class MemexDumper(yaml.SafeDumper):
    """Scoped dumper for memex so we don't mutate global PyYAML state."""
    pass

# Register representers on our dumper (safe + scoped)
MemexDumper.add_representer(FlowList, _represent_flow_seq)

__all__ = ["FlowList", "MemexDumper"]


# === test ===

if __name__ == "__main__":
    data = {
        "task": "write blog",
        "summary": "Today I hacked the planet and wrote the most beautiful README ever. It was legendary.",
        "tags": ["python", "logging", "hacker", "💻"]
    }

    result = dump_no_wrap(data)
    print(result)