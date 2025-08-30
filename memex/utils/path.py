from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

def path_to(*subdirs) -> Path:
    """
    Join subpaths to the repository root.
    Example: path_to('docs', 'git', '2025-07-18-git-privacy.md')
    """
    return REPO_ROOT.joinpath(*subdirs).resolve()

def resolve_pathish(pathish) -> Path:
    """
    Accept a Path or string; return absolute Path.
    - Absolute stays absolute.
    - Relative is resolved to repo root via path_to().
    - Strings can be 'docs/git/2025-07-18-git-privacy.md' or Windows-y ('docs\\git\\2025-07-18-git-privacy.md').
    """
    if isinstance(pathish, Path):
        return pathish if pathish.is_absolute() else path_to(*pathish.parts)

    s = str(pathish).strip()
    # absolute?
    p = Path(s)
    if p.is_absolute():
        return p.resolve()

    parts = s.replace("\\", "/").split("/")
    parts = [p for p in parts if p]  # drop empty from leading/trailing slash
    return path_to(*parts)

if __name__ == "__main__":
    print(resolve_pathish("docs/_data/taxonomy.yml"))