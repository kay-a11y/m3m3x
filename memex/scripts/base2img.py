import base64
import binascii
import re
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Tuple

import click

from memex.utils import log_call
from memex.utils.load import read_basename, read_file, read_path

log = getLogger("memex")

# make assets dir
@log_call()
def _make_assets_dir(files: List[Path]) -> List[Path]:
    """
    For each file, create a sibling assets dir named <basename>.assets
    Return list of created asset dirs.
    """
    dirs: List[Path] = []
    for file in files:
        assets_dir = file.parent / f"{file.stem}.assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        click.secho(f"Created: {assets_dir}", fg="blue")
        dirs.append(assets_dir)
    return dirs

# sniff extension
@log_call()
def _sniff_ext(raw: bytes) -> str:
    """Sniff the extension of decoded base64, return string of extension"""
    ext = (".jpg"  if raw[:3]  == b"\xff\xd8\xff" else
           ".png"  if raw[:8]  == b"\x89PNG\r\n\x1a\n" else
           ".gif"  if raw[:3]  == b"GIF" else
           ".webp" if raw[0:4] == b"RIFF" and raw[8:12] == b"WEBP" else
           ".bin")
    return ext

# catch all inline base64 image entries in one markdown string
@log_call()
def _catch_b64_entries(file_str: str) -> List[Dict[str, str]]:
    """
    catch all inline base64 image entries in one markdown string.
    returns a list of records: {'full': full_markdown, 'alt': alt, 'blob': base64_blob}
    """
    pattern = re.compile(
        r'!\[(?P<alt>[^\]]*)\]\(data:(?P<mime>[^;]+);base64,(?P<blob>[A-Za-z0-9+/=\r\n]+)\)'
    )

    out: List[Dict[str, str]] = []
    for m in pattern.finditer(file_str):
        out.append({
            "full": m.group(0),
            "alt":  m.group("alt"),
            "blob": m.group("blob"),
        })
    return out

# convert
@log_call()
def base2img(entries: List[Dict[str, str]], outdir: Path, prefix: str = "image_") -> List[Tuple[str, str]]:
    """
    decode and save; return replacements [(full_old_link, new_file_link)]
    """
    outdir.mkdir(parents=True, exist_ok=True)
    replacements: List[Tuple[str, str]] = []
    for i, rec in enumerate(entries, 1):
        payload = rec["blob"].replace("\n", "").replace("\r", "")
        try:
            raw = base64.b64decode(payload, validate=True)
        except binascii.Error:
            raw = base64.b64decode(payload)  # fallback

        ext = _sniff_ext(raw)
        outfile = outdir / f"{prefix}{i}{ext}"
        with open(outfile, "wb") as f:
            f.write(raw)
        click.secho(f"[+] Saved {outfile} ({len(raw)/1024/1024:.2f} MB)", fg="blue")

        # rewrite to relative link next to the .md
        rel_link = f"{outdir.name}/{outfile.name}"
        new_md_link = f"![{rec['alt']}]({rel_link})"
        replacements.append((rec["full"], new_md_link))
    return replacements

# rewritten links in markdown
@log_call()
def _rewrite_links(md_text: str, replacements: List[Tuple[str, str]]) -> str:
    """apply replacements back into the markdown string"""
    for old, new in replacements:
        md_text = md_text.replace(old, new)
    return md_text

# === Click command ===
@click.command("base2img")
@click.argument("files", type=click.Path(path_type=Path), required=True)
def base2img_cmd(files: Path) -> None:
    """
    Decode base64 images in Markdown and rewrite links to saved files.
    """
    files = read_path(files) # List[Path]
    asset_dirs = _make_assets_dir(files)
    file_strs = read_file(files) # List[str]

    for md_path, outdir, md_text in zip(files, asset_dirs, file_strs):
        entries = _catch_b64_entries(md_text)
        repls   = base2img(entries, outdir)
        new_md  = _rewrite_links(md_text, repls) # string
        md_path.write_text(new_md, encoding="utf-8")
        click.secho(f"[✓] Rewrote {len(repls)} images in {md_path} → {outdir}", fg="green")