from __future__ import annotations

import shutil
from pathlib import Path

THEME_NAME = "anschmiegcv"


def _assets_root() -> Path:
    return Path(__file__).resolve().parent / "assets"


def _should_copy(src: Path, dst: Path, *, overwrite: bool) -> bool:
    if not dst.exists():
        return True
    if not overwrite:
        return False
    return dst.read_bytes() != src.read_bytes()


def sync_assets(target_root: Path | str, *, overwrite: bool = True) -> list[Path]:
    """Materialize canonical theme + HTML template into a consumer repo root."""
    target = Path(target_root).resolve()
    assets = _assets_root()
    changed: list[Path] = []

    theme_src = assets / THEME_NAME
    html_src = assets / "html"

    if not theme_src.exists() or not html_src.exists():
        raise FileNotFoundError("Shared extension assets are missing from anschmiegcv_tools")

    theme_dst = target / THEME_NAME
    html_dst = target / "html"
    html_file_dst = html_dst / "Full.html"

    theme_dst.mkdir(parents=True, exist_ok=True)
    html_dst.mkdir(parents=True, exist_ok=True)

    for src in sorted(theme_src.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(theme_src)
        dst = theme_dst / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if _should_copy(src, dst, overwrite=overwrite):
            shutil.copy2(src, dst)
            changed.append(dst)

    src_html = html_src / "Full.html"
    if _should_copy(src_html, html_file_dst, overwrite=overwrite):
        shutil.copy2(src_html, html_file_dst)
        changed.append(html_file_dst)

    return changed
