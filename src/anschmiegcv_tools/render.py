from __future__ import annotations

import copy
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import yaml

from .palette import build_semantic_palette
from .sync import sync_assets

KEYWORD_DEFAULT_WEIGHT = 600


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def _section_title_directive_doc() -> str:
    return (
        "Section display mode is controlled in section titles using markdown-style directives, "
        "e.g. 'Skills {#skills .cards}' or 'Certifications {.list}'. "
        "Supported classes: .cards, .list, .timeline."
    )


def _apply_seed_palette(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    design_raw = data.get("design")
    design = design_raw if isinstance(design_raw, dict) else {}
    colors_raw = design.get("colors")
    colors = colors_raw if isinstance(colors_raw, dict) else {}

    seed = colors.get("seed")
    if not isinstance(seed, str) or not seed.strip():
        return data, False

    accent_seed = colors.get("accent_seed")
    accent_seed_value = (
        accent_seed.strip() if isinstance(accent_seed, str) and accent_seed.strip() else None
    )

    palette = build_semantic_palette(seed.strip(), accent_seed=accent_seed_value)

    updated = copy.deepcopy(data)
    updated_design = updated.setdefault("design", {})
    updated_colors = updated_design.setdefault("colors", {})

    updated_colors.pop("seed", None)
    updated_colors.pop("accent_seed", None)

    updated_colors.update(palette)

    return updated, True


def _keyword_pattern(keywords: list[str]) -> re.Pattern[str] | None:
    valid = [kw for kw in keywords if isinstance(kw, str) and kw.strip()]
    if not valid:
        return None
    escaped = [re.escape(kw) for kw in sorted(valid, key=len, reverse=True)]
    return re.compile("(" + "|".join(escaped) + ")")


def _apply_weight_markup(text: str, pattern: re.Pattern[str], weight: int) -> str:
    return pattern.sub(lambda match: f"#text(weight: {weight})[{match.group(0)}]", text)


def _transform_for_keywords(value: Any, pattern: re.Pattern[str], weight: int, key: str | None) -> Any:
    skip_keys = {"start_date", "end_date", "doi", "url"}
    if key in skip_keys:
        return value
    if isinstance(value, str):
        return _apply_weight_markup(value, pattern, weight)
    if isinstance(value, list):
        return [_transform_for_keywords(item, pattern, weight, None) for item in value]
    if isinstance(value, dict):
        return {
            k: _transform_for_keywords(v, pattern, weight, k if isinstance(k, str) else None)
            for k, v in value.items()
        }
    return value


def _apply_keyword_highlighting(data: dict[str, Any]) -> dict[str, Any]:
    settings_raw = data.get("settings")
    settings = settings_raw if isinstance(settings_raw, dict) else {}
    keywords = settings.get("bold_keywords")
    if not isinstance(keywords, list):
        return data

    pattern = _keyword_pattern(keywords)
    if pattern is None:
        return data

    render_settings = settings.get("render_command")
    render_settings = render_settings if isinstance(render_settings, dict) else {}
    weight_raw = render_settings.get("keyword_weight")
    weight = weight_raw if isinstance(weight_raw, int) else KEYWORD_DEFAULT_WEIGHT

    updated = copy.deepcopy(data)
    cv_raw = updated.get("cv")
    if isinstance(cv_raw, dict):
        updated["cv"] = _transform_for_keywords(cv_raw, pattern, weight, None)

    return updated


def _render_one_file(
    yaml_path: Path,
    *,
    extra_rendercv_args: list[str],
    enable_keyword_highlight: bool,
) -> None:
    raw = _load_yaml(yaml_path)

    prepared, has_seed = _apply_seed_palette(raw)
    if enable_keyword_highlight:
        prepared = _apply_keyword_highlighting(prepared)

    suffix = f".{yaml_path.stem}.anschmiegcv.yaml"
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=suffix,
        dir=yaml_path.parent,
        delete=False,
    ) as handle:
        yaml.safe_dump(prepared, handle, sort_keys=False, allow_unicode=True)
        temp_yaml = Path(handle.name)

    try:
        command = ["rendercv", "render", str(temp_yaml), *extra_rendercv_args]
        subprocess.run(command, check=True)
        if has_seed:
            print(f"[anschmiegcv] Applied generated palette for {yaml_path.name}")
    finally:
        temp_yaml.unlink(missing_ok=True)


def render_yaml_files(
    files: list[Path],
    *,
    cwd: Path,
    sync_before_render: bool = True,
    enable_keyword_highlight: bool = False,
    extra_rendercv_args: list[str] | None = None,
) -> None:
    """Render YAML files through RenderCV after applying anschmiegcv preprocessing."""
    if sync_before_render:
        changed = sync_assets(cwd)
        if changed:
            print(f"[anschmiegcv] Synced {len(changed)} shared asset file(s)")

    if not files:
        files = sorted(cwd.glob("*_CV.yaml"))

    if not files:
        raise FileNotFoundError("No *_CV.yaml files found")

    extras = extra_rendercv_args or []
    for file_path in files:
        resolved = file_path if file_path.is_absolute() else cwd / file_path
        _render_one_file(
            resolved,
            extra_rendercv_args=extras,
            enable_keyword_highlight=enable_keyword_highlight,
        )

    print("[anschmiegcv] Render complete")
    print("[anschmiegcv] " + _section_title_directive_doc())
