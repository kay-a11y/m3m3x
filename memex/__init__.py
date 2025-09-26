import tomllib

from memex.utils.path import resolve_pathish


def get_version() -> str:
    try:
        pyproject = resolve_pathish("pyproject.toml")
        with open(pyproject, "rb") as f:
            return tomllib.load(f)["project"]["version"]
    except Exception:
        return "0.0.0-dev"

__version__ = get_version()
