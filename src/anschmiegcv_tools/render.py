from __future__ import annotations

import sys

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

# Default design config filename
DESIGN_CONFIG_FILENAME = "design_config.yaml"


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


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Deep merge overlay into base, with overlay taking precedence."""
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _merge_with_design_config(cv_data: dict[str, Any], cv_path: Path) -> dict[str, Any]:
    """Merge CV content with design config if it exists."""
    design_path = cv_path.parent / DESIGN_CONFIG_FILENAME
    if not design_path.exists():
        return cv_data
    
    design_data = _load_yaml(design_path)
    # Design config provides defaults, CV content overrides
    merged = _deep_merge(design_data, cv_data)
    return merged


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


def _extract_education_style(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Extract style from education_entry template, returning (data_without_style, style_config).

    RenderCV's schema doesn't allow custom style fields, so we need to remove it
    before validation and use it for post-processing.
    """
    design = data.get("design")
    if not isinstance(design, dict):
        return data, None

    templates = design.get("templates")
    if not isinstance(templates, dict):
        return data, None

    education_entry = templates.get("education_entry")
    if not isinstance(education_entry, dict):
        return data, None

    style = education_entry.get("style")
    if style is None:
        return data, None

    # Create a copy without the style field
    updated = copy.deepcopy(data)
    updated.get("design", {}).get("templates", {}).get("education_entry", {}).pop("style", None)
    return updated, style


def _extract_cards_config(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Extract cards styling config, returning (data_without_cards, cards_config).

    RenderCV's schema doesn't allow custom styling fields, so we need to remove it
    before validation and use it for post-processing.
    """
    design = data.get("design")
    if not isinstance(design, dict):
        return data, None

    cards = design.get("cards")
    if not isinstance(cards, dict):
        return data, None

    # Create a copy without the cards field
    updated = copy.deepcopy(data)
    updated.get("design", {}).pop("cards", None)
    return updated, cards


def _extract_timeline_config(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Extract timeline styling config, returning (data_without_timeline, timeline_config).

    RenderCV's schema doesn't allow custom styling fields, so we need to remove it
    before validation and use it for post-processing.
    """
    design = data.get("design")
    if not isinstance(design, dict):
        return data, None

    timeline = design.get("timeline")
    if not isinstance(timeline, dict):
        return data, None

    # Create a copy without the timeline field
    updated = copy.deepcopy(data)
    updated.get("design", {}).pop("timeline", None)
    return updated, timeline


def _extract_page_background_color(data: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    """Extract page.background_color, returning (data_without_bg, bg_color).

    RenderCV's schema doesn't allow custom page fields, so we need to remove it
    before validation and use it for post-processing.
    """
    design = data.get("design")
    if not isinstance(design, dict):
        return data, None

    page = design.get("page")
    if not isinstance(page, dict):
        return data, None

    bg_color = page.get("background_color")
    if bg_color is None:
        return data, None

    # Create a copy without the background_color field
    updated = copy.deepcopy(data)
    updated.get("design", {}).get("page", {}).pop("background_color", None)
    return updated, bg_color


def _find_typst_output(yaml_path: Path, yaml_data: dict[str, Any]) -> Path | None:
    """Find the generated Typst file for a CV YAML file.

    The output filename is based on cv.name, not the YAML filename.
    """
    cv_data = yaml_data.get("cv", {})
    cv_name = cv_data.get("name", "")
    if cv_name:
        # Convert "Joe Mama" to "Joe_Mama_CV.typ"
        name_slug = cv_name.replace(" ", "_")
        candidate = yaml_path.parent / "rendercv_output" / f"{name_slug}_CV.typ"
        if candidate.exists():
            return candidate

    # Fallback: find the most recent .typ file in rendercv_output
    output_dir = yaml_path.parent / "rendercv_output"
    if output_dir.is_dir():
        typst_files = list(output_dir.glob("*.typ"))
        if typst_files:
            # Return the most recently modified one
            return max(typst_files, key=lambda p: p.stat().st_mtime)
    return None


def _recompile_pdf(typst_path: Path) -> None:
    """Re-compile the Typst file to PDF after modifications."""
    import shutil

    # Find typst compiler
    typst_cmd = shutil.which("typst")
    if typst_cmd is None:
        print("[anschmiegcv] Warning: typst not found, skipping PDF re-compilation")
        return

    pdf_path = typst_path.with_suffix(".pdf")

    try:
        subprocess.run(
            [typst_cmd, "compile", str(typst_path), str(pdf_path)],
            check=True,
            capture_output=True,
        )
        print(f"[anschmiegcv] Re-compiled PDF with education style")
    except subprocess.CalledProcessError as e:
        print(f"[anschmiegcv] Warning: Failed to re-compile PDF: {e.stderr.decode() if e.stderr else str(e)}")


def _inject_education_style(typst_path: Path, education_style: dict[str, Any], colors: dict[str, Any]) -> None:
    """Replace education_style variable defaults in the Typst file with configured values.

    The Preamble defines default values for education styling variables.
    This function replaces them with values from design_config.yaml.
    """
    # Resolve color references
    def resolve_color(color_ref: str) -> str:
        """Convert 'text' to footer color RGB, 'primary' to name color RGB."""
        if color_ref == "text":
            # Use footer color (grey)
            if "footer" in colors and hasattr(colors["footer"], "as_rgb"):
                return colors["footer"].as_rgb()
            return "rgb(39, 57, 59)"  # Default grey
        elif color_ref == "primary":
            # Use name color (teal/theme)
            if "name" in colors and hasattr(colors["name"], "as_rgb"):
                return colors["name"].as_rgb()
            return "rgb(0, 120, 135)"  # Default teal
        return f'rgb("{color_ref}")'

    degree_style = education_style.get("degree", {})
    area_style = education_style.get("area", {})
    institution_style = education_style.get("institution", {})

    degree_color = resolve_color(degree_style.get("color", "text"))
    degree_weight = degree_style.get("weight", 600)
    area_color = resolve_color(area_style.get("color", "text"))
    area_weight = area_style.get("weight", 700)
    institution_color = resolve_color(institution_style.get("color", "primary"))
    institution_weight = institution_style.get("weight", 600)

    # Read the Typst file
    content = typst_path.read_text(encoding="utf-8")

    # Replace each variable definition line
    # The Preamble defines these with defaults; we override with configured values
    import re

    replacements = [
        (r'#let anschmiegcv_education_degree_color = rgb\([^)]+\)', f'#let anschmiegcv_education_degree_color = {degree_color}'),
        (r'#let anschmiegcv_education_degree_weight = \d+', f'#let anschmiegcv_education_degree_weight = {degree_weight}'),
        (r'#let anschmiegcv_education_area_color = rgb\([^)]+\)', f'#let anschmiegcv_education_area_color = {area_color}'),
        (r'#let anschmiegcv_education_area_weight = \d+', f'#let anschmiegcv_education_area_weight = {area_weight}'),
        (r'#let anschmiegcv_education_institution_color = rgb\([^)]+\)', f'#let anschmiegcv_education_institution_color = {institution_color}'),
        (r'#let anschmiegcv_education_institution_weight = \d+', f'#let anschmiegcv_education_institution_weight = {institution_weight}'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    typst_path.write_text(content, encoding="utf-8")


def _find_html_output(yaml_path: Path, yaml_data: dict[str, Any]) -> Path | None:
    """Find the generated HTML file for a CV YAML file.

    The output filename is based on cv.name, not the YAML filename.
    """
    cv_data = yaml_data.get("cv", {})
    cv_name = cv_data.get("name", "")
    if cv_name:
        name_slug = cv_name.replace(" ", "_")
        candidate = yaml_path.parent / "rendercv_output" / f"{name_slug}_CV.html"
        if candidate.exists():
            return candidate

    # Fallback: find the most recent .html file in rendercv_output
    output_dir = yaml_path.parent / "rendercv_output"
    if output_dir.is_dir():
        html_files = list(output_dir.glob("*.html"))
        if html_files:
            return max(html_files, key=lambda p: p.stat().st_mtime)
    return None


def _inject_education_style_html(html_path: Path, education_style: dict[str, Any], colors: dict[str, Any]) -> None:
    """Inject education CSS variable values into the generated HTML file.

    The HTML template defines default --cv-education-* CSS variables. This function
    replaces those default values with the configured values from design_config.yaml,
    matching the same color resolution logic used for the Typst/PDF output.
    """
    def resolve_color_css(color_ref: str) -> str:
        """Convert 'text' to footer color RGB string, 'primary' to name color RGB string."""
        if color_ref == "text":
            if "footer" in colors and hasattr(colors["footer"], "as_rgb"):
                return colors["footer"].as_rgb()
            return "rgb(39, 57, 59)"
        elif color_ref == "primary":
            if "name" in colors and hasattr(colors["name"], "as_rgb"):
                return colors["name"].as_rgb()
            return "rgb(0, 120, 135)"
        return color_ref

    degree_style = education_style.get("degree", {})
    area_style = education_style.get("area", {})
    institution_style = education_style.get("institution", {})

    area_color = resolve_color_css(area_style.get("color", "text"))
    area_weight = area_style.get("weight", 700)
    degree_color = resolve_color_css(degree_style.get("color", "text"))
    degree_weight = degree_style.get("weight", 600)
    institution_color = resolve_color_css(institution_style.get("color", "primary"))
    institution_weight = institution_style.get("weight", 600)

    content = html_path.read_text(encoding="utf-8")

    replacements = [
        (r'--cv-education-area:\s*[^;]+;', f'--cv-education-area: {area_color};'),
        (r'--cv-education-area-weight:\s*\d+;', f'--cv-education-area-weight: {area_weight};'),
        (r'--cv-education-degree:\s*[^;]+;', f'--cv-education-degree: {degree_color};'),
        (r'--cv-education-degree-weight:\s*\d+;', f'--cv-education-degree-weight: {degree_weight};'),
        (r'--cv-education-institution:\s*[^;]+;', f'--cv-education-institution: {institution_color};'),
        (r'--cv-education-institution-weight:\s*\d+;', f'--cv-education-institution-weight: {institution_weight};'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    html_path.write_text(content, encoding="utf-8")


def _inject_cards_style_html(html_path: Path, cards_config: dict[str, Any]) -> None:
    """Inject cards CSS variable values into the generated HTML file.

    The HTML template defines default --cv-card-* CSS variables. This function
    replaces those default values with the configured values from design_config.yaml.
    """
    if not cards_config:
        return

    # Convert config values to CSS-acceptable values
    # Config uses pt/cm for PDF, HTML needs px or rem

    def convert_to_px(val: str) -> str:
        """Convert pt or cm to px for CSS."""
        if isinstance(val, str):
            if val.endswith("pt"):
                try:
                    pt_val = float(val[:-2])
                    return f"{round(pt_val * 1.33)}px"
                except ValueError:
                    pass
            elif val.endswith("cm"):
                try:
                    cm_val = float(val[:-2])
                    return f"{round(cm_val * 37.795)}px"  # 1cm = 37.795px at 96dpi
                except ValueError:
                    pass
        return val  # Return as-is if no conversion needed

    border_radius = convert_to_px(cards_config.get("border_radius", "8pt"))
    border_width = convert_to_px(cards_config.get("border_width", "1pt"))
    gap = convert_to_px(cards_config.get("gap", "0.24cm"))
    padding = convert_to_px(cards_config.get("padding", "8pt"))

    content = html_path.read_text(encoding="utf-8")

    replacements = [
        (r'--cv-card-border-radius:\s*[^;]+;', f'--cv-card-border-radius: {border_radius};'),
        (r'--cv-card-border-width:\s*[^;]+;', f'--cv-card-border-width: {border_width};'),
        (r'--cv-card-gap:\s*[^;]+;', f'--cv-card-gap: {gap};'),
        (r'--cv-card-padding:\s*[^;]+;', f'--cv-card-padding: {padding};'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    html_path.write_text(content, encoding="utf-8")


def _inject_timeline_style_html(html_path: Path, timeline_config: dict[str, Any]) -> None:
    """Inject timeline CSS variable values into the generated HTML file.

    The HTML template defines default --cv-timeline-* CSS variables. This function
    replaces those default values with the configured values from design_config.yaml.
    """
    if not timeline_config:
        return

    def convert_to_px(val: str) -> str:
        """Convert pt to px for CSS."""
        if isinstance(val, str):
            if val.endswith("pt"):
                try:
                    pt_val = float(val[:-2])
                    return f"{round(pt_val * 1.33)}px"
                except ValueError:
                    pass
        return val  # Return as-is if no conversion needed (e.g., already in px)

    dot_size = convert_to_px(timeline_config.get("dot_size", "14pt"))
    line_width = convert_to_px(timeline_config.get("line_width", "2pt"))

    content = html_path.read_text(encoding="utf-8")

    replacements = [
        (r'--cv-timeline-dot-size:\s*[^;]+;', f'--cv-timeline-dot-size: {dot_size};'),
        (r'--cv-timeline-line-width:\s*[^;]+;', f'--cv-timeline-line-width: {line_width};'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    html_path.write_text(content, encoding="utf-8")


def _inject_background_color_html(html_path: Path, bg_color: str) -> None:
    """Inject background color into the generated HTML file.

    The HTML template defines a default --cv-background CSS variable.
    This function replaces it with the configured value from design_config.yaml.
    """
    content = html_path.read_text(encoding="utf-8")

    # Replace the background color variable
    content = re.sub(
        r'--cv-background:\s*[^;]+;',
        f'--cv-background: {bg_color};',
        content
    )

    html_path.write_text(content, encoding="utf-8")


def _render_one_file(
    yaml_path: Path,
    *,
    extra_rendercv_args: list[str],
    enable_keyword_highlight: bool,
) -> None:
    raw = _load_yaml(yaml_path)

    # Merge with design config if it exists
    merged = _merge_with_design_config(raw, yaml_path)

    prepared, has_seed = _apply_seed_palette(merged)
    prepared, has_adaptive_cards = _apply_adaptive_cards_layout(prepared)
    if enable_keyword_highlight:
        prepared = _apply_keyword_highlighting(prepared)

    # Extract education_style before passing to rendercv (schema doesn't allow it)
    prepared, education_style = _extract_education_style(prepared)

    # Extract cards styling config before passing to rendercv (schema doesn't allow it)
    prepared, cards_config = _extract_cards_config(prepared)

    # Extract timeline styling config before passing to rendercv (schema doesn't allow it)
    prepared, timeline_config = _extract_timeline_config(prepared)

    # Extract page background_color before passing to rendercv (schema doesn't allow it)
    prepared, background_color = _extract_page_background_color(prepared)

    # Keep colors for resolving color references
    design_colors = prepared.get("design", {}).get("colors", {})

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
        command = [sys.executable, "-m", "rendercv", "render", str(temp_yaml), *extra_rendercv_args]
        subprocess.run(command, check=True)
        if has_seed:
            print(f"[anschmiegcv] Applied generated palette for {yaml_path.name}")
        if has_adaptive_cards:
            print(f"[anschmiegcv] Applied adaptive cards layout for {yaml_path.name}")

        # Inject education_style into generated Typst and re-compile PDF
        if education_style:
            typst_path = _find_typst_output(yaml_path, prepared)
            if typst_path and typst_path.exists():
                _inject_education_style(typst_path, education_style, design_colors)
                print(f"[anschmiegcv] Applied education style for {yaml_path.name}")
                # Re-compile PDF since we modified the Typst
                _recompile_pdf(typst_path)

            # Also inject education CSS variables into the generated HTML
            html_path = _find_html_output(yaml_path, prepared)
            if html_path and html_path.exists():
                _inject_education_style_html(html_path, education_style, design_colors)
                print(f"[anschmiegcv] Applied education style to HTML for {yaml_path.name}")

        # Inject cards styling into HTML
        if cards_config:
            html_path = _find_html_output(yaml_path, prepared)
            if html_path and html_path.exists():
                _inject_cards_style_html(html_path, cards_config)
                print(f"[anschmiegcv] Applied cards style to HTML for {yaml_path.name}")

        # Inject timeline styling into HTML
        if timeline_config:
            html_path = _find_html_output(yaml_path, prepared)
            if html_path and html_path.exists():
                _inject_timeline_style_html(html_path, timeline_config)
                print(f"[anschmiegcv] Applied timeline style to HTML for {yaml_path.name}")

        # Inject background color into HTML
        if background_color:
            html_path = _find_html_output(yaml_path, prepared)
            if html_path and html_path.exists():
                _inject_background_color_html(html_path, background_color)
                print(f"[anschmiegcv] Applied background color to HTML for {yaml_path.name}")
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
