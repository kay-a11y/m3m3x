from __future__ import annotations

import re

_REPLACE = {
    '‘': "'", '’': "'", '“': '"', '”': '"',
    '—': '-', ' ': ' ', ' ':' ', ' ': ' ', 
    '–': '-', '‑': '-',
}
_PATTERN = re.compile("|".join(map(re.escape, _REPLACE)))

def clean_punctuation(text: str) -> str:
    """Return *text* with fancy Unicode punctuation normalized to ASCII/basic."""
    return _PATTERN.sub(lambda m: _REPLACE[m.group()], text)

__all__ = ["clean_punctuation"]
