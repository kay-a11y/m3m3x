"""
memex.utils.symbols - Common Unicode symbols for CLI output
===========================================================

Centralized constants so all commands use consistent
status markers (success, warnings, errors, prompts).
"""

# Status
CHECK = "✔"   # U+2714: success / done
FAIL  = "✘"   # U+2718: error / failure
WARN  = "⚠"   # U+26A0: warning / caution

# Flow / navigation
ARROW = "➜"   # U+279C: next step / pointer
ELLIP = "…"   # U+2026: processing / waiting

# Prompts
QMARK = "?"   # ASCII 0x3F: question
EXCL   = "!"  # ASCII 0x21: exclamation
EXCL2  = "‼"  # U+203C: double exclamation

# Add/remove
PLUS  = "+"
MINUS = "-" 

# File/tree
TRIANGLE = "▸"  # U+25B8: file/folder arrow
VERTICAL = "│"  # U+2502: vertical bar
CORNER   = "└"  # U+2514: corner

__all__ = [
    "CHECK", "FAIL", "WARN",
    "ARROW", "ELLIP",
    "QMARK", "EXCL", "EXCL2",
    "PLUS", "MINUS",
    "TRIANGLE", "VERTICAL", "CORNER",
]
