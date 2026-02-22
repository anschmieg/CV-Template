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
SECTION_TITLE_DIRECTIVE_PATTERN = re.compile(r"^(?P<title>.*?)(?:\s*\{(?P<directive>[^{}]*)\})?\s*$")
CARDS_LAYOUT_CLASS_PATTERN = re.compile(r"^\.cards-(?:1|2|3|4|3w)$")


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
        "Supported classes: .cards, .list, .timeline. "
        "Cards sections are auto-tuned per section with layout classes "
        "(.cards-1/.cards-2/.cards-3/.cards-3w/.cards-4)."
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


def _estimate_text_weight(value: Any) -> float:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0.0
        return float(len(text) + text.count("\n") * 18)
    if isinstance(value, list):
        total = 0.0
        for item in value:
            item_weight = _estimate_text_weight(item)
            if item_weight > 0:
                total += item_weight + 20.0
        return total
    return 0.0


def _estimate_card_density(entry: dict[str, Any]) -> float:
    primary_fields = (
        "title",
        "name",
        "label",
        "company",
        "institution",
        "position",
        "area",
        "degree",
        "journal",
        "publisher",
        "venue",
        "booktitle",
        "conference",
    )
    detail_fields = ("summary", "details", "citation")
    list_fields = ("highlights", "authors")
    meta_fields = ("date", "start_date", "end_date", "location", "url", "doi")

    score = 0.0

    for key in primary_fields:
        weight = _estimate_text_weight(entry.get(key))
        if weight > 0:
            score += weight / 44.0 + 0.35

    for key in detail_fields:
        weight = _estimate_text_weight(entry.get(key))
        if weight > 0:
            score += weight / 50.0 + 0.8

    for key in list_fields:
        value = entry.get(key)
        if isinstance(value, list):
            for item in value:
                item_weight = _estimate_text_weight(item)
                if item_weight > 0:
                    score += item_weight / 58.0 + 0.85

    for key in meta_fields:
        weight = _estimate_text_weight(entry.get(key))
        if weight > 0:
            score += weight / 72.0 + 0.2

    return max(score, 1.0)


def _select_cards_layout(scores: list[float]) -> str:
    count = len(scores)
    if count <= 1:
        return "1"

    avg_score = sum(scores) / count
    max_score = max(scores)
    spread = max_score / max(avg_score, 0.01)

    # High-density sections should stay single or two-column for readability.
    if avg_score >= 17.0 or max_score >= 24.0:
        return "1"
    if avg_score >= 12.5 or max_score >= 18.0:
        return "2"

    # Very light content can use more columns.
    if count >= 4 and avg_score <= 7.2 and max_score <= 10.5:
        return "4"

    if count == 3:
        # On A4 PDF pages, three columns are only readable for genuinely light cards.
        if avg_score <= 8.6 and max_score <= 10.4:
            return "3"
        if avg_score <= 9.2 and spread >= 1.5 and max_score <= 11.2:
            return "3w"
        return "2"

    if count >= 3 and avg_score <= 9.5:
        if spread >= 1.55 and max_score >= 8.5:
            return "3w"
        if count >= 4 and max_score <= 13.0:
            return "4"
        return "3"

    if count >= 4 and avg_score <= 11.0:
        return "3"

    return "2"


def _apply_cards_layout_class(section_title: str, layout: str) -> str:
    match = SECTION_TITLE_DIRECTIVE_PATTERN.match(section_title)
    if match is None:
        return section_title

    title = (match.group("title") or "").strip()
    directive = (match.group("directive") or "").strip()
    tokens = directive.split() if directive else []

    has_cards = any(token == ".cards" or token.startswith(".cards-") for token in tokens)
    if not has_cards:
        return section_title

    cleaned_tokens = [token for token in tokens if not CARDS_LAYOUT_CLASS_PATTERN.fullmatch(token)]
    cleaned_tokens.append(f".cards-{layout}")
    directive_value = " ".join(cleaned_tokens)
    return f"{title} {{{directive_value}}}"


def _apply_adaptive_cards_layout(data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    cv = data.get("cv")
    if not isinstance(cv, dict):
        return data, False

    sections = cv.get("sections")
    if not isinstance(sections, dict):
        return data, False

    changed = False
    updated_sections: dict[str, Any] = {}

    for section_title, section_content in sections.items():
        new_title = section_title
        if isinstance(section_title, str) and ".cards" in section_title and isinstance(section_content, list):
            entries = [item for item in section_content if isinstance(item, dict)]
            if entries:
                scores = [_estimate_card_density(entry) for entry in entries]
                layout = _select_cards_layout(scores)
                new_title = _apply_cards_layout_class(section_title, layout)

        updated_sections[new_title] = section_content
        changed = changed or (new_title != section_title)

    if not changed:
        return data, False

    updated = copy.deepcopy(data)
    updated_cv = updated.get("cv")
    if isinstance(updated_cv, dict):
        updated_cv["sections"] = updated_sections

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
    prepared, has_adaptive_cards = _apply_adaptive_cards_layout(prepared)
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
        if has_adaptive_cards:
            print(f"[anschmiegcv] Applied adaptive cards layout for {yaml_path.name}")
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
