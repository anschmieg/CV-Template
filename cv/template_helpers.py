from __future__ import annotations

import copy
import html
import re
from collections.abc import Iterable
from typing import Any


_DIRECTIVE_BLOCK_PATTERN = re.compile(r"\{([^{}]+)\}")
_LEADING_DIRECTIVE_PATTERN = re.compile(r"^\s*\{([^{}]+)\}\s*")
_SPAN_CLASS_PATTERN = re.compile(r"\[([^\]]*?)\]\{([^{}]+)\}")
_LIST_LINE_PATTERN = re.compile(r"^\s*(?:[-+*]\s+|\d+\.\s+)")
_BODY_PLACEHOLDERS = {
    "SUMMARY",
    "HIGHLIGHTS",
    "DETAILS",
    "AUTHORS",
    "URL",
    "DOI",
    "JOURNAL",
}
_WEIGHT_ALIASES = {
    "thin": "100",
    "extra_light": "200",
    "extralight": "200",
    "light": "300",
    "normal": "400",
    "regular": "400",
    "medium": "500",
    "semi_bold": "600",
    "semibold": "600",
    "demi_bold": "600",
    "demibold": "600",
    "bold": "700",
    "extra_bold": "800",
    "extrabold": "800",
    "black": "900",
}
_CLASS_STYLE_ALIASES = {
    "italic": {"style": "italic"},
    "underline": {"decoration": "underline"},
    "regular": {"weight": "400"},
    "normal": {"weight": "400"},
    "medium": {"weight": "500"},
    "semibold": {"weight": "600"},
    "semi_bold": {"weight": "600"},
    "bold": {"weight": "700"},
    "light": {"weight": "300"},
    "thin": {"weight": "100"},
}


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip("\n")


def _normalize_span_markup(value: str) -> str:
    return value.replace(r"\[", "[").replace(r"\]", "]").replace(r"\_", "_")


def _resolve_color(design: Any, color_value: str | None) -> str | None:
    if color_value is None:
        return None

    color_key = color_value.strip().replace("\\_", "_")
    if not color_key:
        return None

    colors = getattr(design, "colors", None)
    if colors is not None and hasattr(colors, color_key):
        resolved = getattr(colors, color_key)
        if resolved is not None and hasattr(resolved, "as_rgb"):
            return resolved.as_rgb()

    return color_key


def _normalize_style_key(key: str) -> str:
    normalized = key.strip().lower().replace("\\_", "_").replace("-", "_").replace(" ", "_")
    return {
        "font_weight": "weight",
        "font_style": "style",
        "font_size": "size",
        "text_decoration": "decoration",
    }.get(normalized, normalized)


def _normalize_style_value(design: Any, key: str, value: str) -> str:
    normalized_key = _normalize_style_key(key)
    normalized_value = value.strip().replace("\\_", "_")

    if normalized_key == "color":
        return _resolve_color(design, normalized_value) or normalized_value

    if normalized_key in {"font_weight", "weight"}:
        alias_key = normalized_value.lower().replace("-", "_").replace(" ", "_")
        return _WEIGHT_ALIASES.get(alias_key, normalized_value)

    if normalized_key in {"style", "font_style"}:
        style_key = normalized_value.lower().replace("-", "_").replace(" ", "_")
        if style_key in {"italic", "oblique"}:
            return "italic"
        return "normal"

    if normalized_key in {"font_size", "size", "text_decoration", "decoration"}:
        return normalized_value

    return normalized_value


def _split_directive_items(content: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    paren_depth = 0

    for char in content:
        if char == "(":
            paren_depth += 1
        elif char == ")" and paren_depth > 0:
            paren_depth -= 1

        if char in {",", ";"} and paren_depth == 0:
            item = "".join(current).strip()
            if item:
                parts.append(item)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)

    return parts


def _parse_style_directive(content: str, design: Any) -> dict[str, str]:
    directive_style: dict[str, str] = {}

    for item in _split_directive_items(content):
        if ":" not in item:
            continue

        key, value = item.split(":", 1)
        normalized_key = _normalize_style_key(key)
        if not normalized_key:
            continue

        directive_style[normalized_key] = _normalize_style_value(
            design, normalized_key, value
        )

    return directive_style


def _parse_style_classes(content: str, design: Any) -> dict[str, str]:
    class_style: dict[str, str] = {}

    for raw_token in content.split():
        if not raw_token.startswith("."):
            continue

        token = raw_token[1:].strip()
        normalized = _normalize_style_key(token)
        if not normalized:
            continue

        if normalized in _CLASS_STYLE_ALIASES:
            class_style.update(_CLASS_STYLE_ALIASES[normalized])
            continue

        if normalized.startswith("color_"):
            color_token = normalized[len("color_") :].replace("_", "-")
            class_style["color"] = _resolve_color(design, color_token.replace("-", "_")) or color_token
            continue

        if normalized.startswith("weight_"):
            class_style["weight"] = normalized[len("weight_") :]
            continue

        if re.fullmatch(r"w\d{3}", normalized):
            class_style["weight"] = normalized[1:]
            continue

    return class_style


def _extract_leading_style_directives(
    line: str, design: Any
) -> tuple[str, dict[str, str]]:
    remaining = line
    style: dict[str, str] = {}

    while True:
        match = _LEADING_DIRECTIVE_PATTERN.match(remaining)
        if match is None:
            break

        style.update(_parse_style_directive(match.group(1), design))
        remaining = remaining[match.end() :]

    return remaining, style


def _strip_inline_directives(value: str) -> str:
    return _DIRECTIVE_BLOCK_PATTERN.sub("", _normalize_span_markup(value))


def _strip_span_classes(value: str) -> str:
    return _SPAN_CLASS_PATTERN.sub(lambda match: match.group(1), _normalize_span_markup(value))


def parse_styled_segments(
    value: Any,
    design: Any,
    base_style: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    text = _normalize_span_markup(str(value or ""))
    if not text:
        return []

    segments: list[dict[str, Any]] = []
    current_style = dict(base_style or {})
    cursor = 0

    while cursor < len(text):
        directive_match = _DIRECTIVE_BLOCK_PATTERN.search(text, cursor)
        span_match = _SPAN_CLASS_PATTERN.search(text, cursor)

        matches = [m for m in (directive_match, span_match) if m is not None]
        if not matches:
            tail = text[cursor:]
            if tail:
                segments.append({"text": tail, "style": current_style.copy()})
            break

        match = min(matches, key=lambda item: item.start())
        chunk = text[cursor : match.start()]
        if chunk:
            segments.append({"text": chunk, "style": current_style.copy()})

        if match.re is _SPAN_CLASS_PATTERN:
            span_style = current_style.copy()
            span_style.update(_parse_style_classes(match.group(2), design))
            segments.append({"text": match.group(1), "style": span_style})
        else:
            current_style.update(_parse_style_directive(match.group(1), design))

        cursor = match.end()

    if not segments:
        return [
            {
                "text": _strip_span_classes(_strip_inline_directives(text)),
                "style": current_style.copy(),
            }
        ]

    return segments


def parse_styled_blocks(value: Any, design: Any) -> list[dict[str, Any]]:
    text = _normalize_text(value)
    if not text:
        return []

    blocks: list[dict[str, Any]] = []
    list_lines: list[str] = []
    list_style: dict[str, str] | None = None

    def flush_list() -> None:
        nonlocal list_lines, list_style
        if list_lines:
            blocks.append(
                {
                    "type": "markdown",
                    "text": "\n".join(list_lines),
                    "style": dict(list_style or {}),
                }
            )
            list_lines = []
            list_style = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            flush_list()
            continue

        cleaned_line, line_style = _extract_leading_style_directives(raw_line, design)
        if _LIST_LINE_PATTERN.match(cleaned_line):
            if not list_lines:
                list_style = dict(line_style)
            list_lines.append(_strip_span_classes(_strip_inline_directives(cleaned_line)).rstrip())
            continue

        flush_list()
        blocks.append(
            {
                "type": "line",
                "text": _strip_span_classes(_strip_inline_directives(cleaned_line)).strip(),
                "style": dict(line_style),
                "segments": parse_styled_segments(cleaned_line.strip(), design, line_style),
            }
        )

    flush_list()
    return blocks


def count_header_lines(template_text: Any) -> int:
    text = _normalize_text(template_text)
    if not text:
        return 0

    count = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        cleaned_line = _strip_inline_directives(
            _LEADING_DIRECTIVE_PATTERN.sub("", line)
        ).strip()
        cleaned_line = _strip_span_classes(cleaned_line)
        if any(placeholder in cleaned_line for placeholder in _BODY_PLACEHOLDERS):
            break
        count += 1

    return count


def entry_main_template(entry: Any, design: Any) -> str:
    templates = getattr(design, "templates", None)
    if templates is None:
        return ""

    if getattr(entry, "company", None) and hasattr(templates, "experience_entry"):
        return getattr(templates.experience_entry, "main_column", "") or ""

    if getattr(entry, "institution", None) and hasattr(templates, "education_entry"):
        return getattr(templates.education_entry, "main_column", "") or ""

    if getattr(entry, "doi", None) or getattr(entry, "journal", None):
        if hasattr(templates, "publication_entry"):
            return getattr(templates.publication_entry, "main_column", "") or ""

    if hasattr(entry, "name") and hasattr(templates, "normal_entry"):
        return getattr(templates.normal_entry, "main_column", "") or ""

    return ""


def entry_date_template(entry: Any, design: Any) -> str:
    templates = getattr(design, "templates", None)
    if templates is None:
        return ""

    if getattr(entry, "company", None) and hasattr(templates, "experience_entry"):
        return getattr(templates.experience_entry, "date_and_location_column", "") or ""

    if getattr(entry, "institution", None) and hasattr(templates, "education_entry"):
        return getattr(templates.education_entry, "date_and_location_column", "") or ""

    if getattr(entry, "doi", None) or getattr(entry, "journal", None):
        if hasattr(templates, "publication_entry"):
            return getattr(templates.publication_entry, "date_and_location_column", "") or ""

    if hasattr(entry, "name") and hasattr(templates, "normal_entry"):
        return getattr(templates.normal_entry, "date_and_location_column", "") or ""

    return ""


def body_is_in_main_column(template_text: Any) -> bool:
    text = _normalize_text(template_text)
    if not text:
        return False
    return any(placeholder in text for placeholder in _BODY_PLACEHOLDERS)


def remaining_blocks(
    blocks: Iterable[dict[str, Any]], header_count: int
) -> list[dict[str, Any]]:
    return list(blocks)[header_count:]


def _string_or_none(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def typst_text_options(
    style: dict[str, str] | None = None,
    *,
    default_color: str | None = None,
    default_weight: str | int | None = None,
    default_size: str | None = None,
    default_font_style: str | None = None,
) -> str:
    style = style or {}
    options: list[str] = []

    color = _string_or_none(style.get("color")) or _string_or_none(default_color)
    weight = _string_or_none(style.get("weight") or style.get("font_weight")) or _string_or_none(
        str(default_weight) if default_weight is not None else None
    )
    size = _string_or_none(style.get("size") or style.get("font_size")) or _string_or_none(default_size)
    font_style = _string_or_none(style.get("style") or style.get("font_style")) or _string_or_none(default_font_style)

    if color:
        options.append(f"fill: {color}")
    if weight:
        options.append(f"weight: {weight}")
    if size:
        options.append(f"size: {size}")
    if font_style and font_style != "normal":
        options.append(f'style: "{font_style}"')

    return ", ".join(options)


def html_style(
    style: dict[str, str] | None = None,
    *,
    default_color: str | None = None,
    default_weight: str | int | None = None,
    default_font_style: str | None = None,
    default_size: str | None = None,
    default_decoration: str | None = None,
) -> str:
    style = style or {}
    css_rules: list[str] = []

    color = _string_or_none(style.get("color")) or _string_or_none(default_color)
    weight = _string_or_none(style.get("weight") or style.get("font_weight")) or _string_or_none(
        str(default_weight) if default_weight is not None else None
    )
    font_style = _string_or_none(style.get("style") or style.get("font_style")) or _string_or_none(default_font_style)
    font_size = _string_or_none(style.get("size") or style.get("font_size")) or _string_or_none(default_size)
    decoration = _string_or_none(style.get("decoration") or style.get("text_decoration")) or _string_or_none(default_decoration)

    if color:
        css_rules.append(f"color: {color}")
    if weight:
        css_rules.append(f"font-weight: {weight}")
    if font_style and font_style != "normal":
        css_rules.append(f"font-style: {font_style}")
    if font_size:
        css_rules.append(f"font-size: {font_size}")
    if decoration:
        css_rules.append(f"text-decoration: {decoration}")

    return "; ".join(css_rules)


def _safe_link(raw_url: str) -> str:
    candidate = (raw_url or "").strip()
    if not candidate:
        return "#"

    lower = candidate.lower()
    if lower.startswith(("http://", "https://", "mailto:", "tel:")):
        return html.escape(candidate, quote=True)

    return "#"


def html_inline_markdown(value: Any) -> str:
    text = str(value or "")
    if not text:
        return ""

    text = _SPAN_CLASS_PATTERN.sub(lambda match: match.group(1), text)
    rendered = html.escape(text)
    rendered = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda match: (
            f'<a href="{_safe_link(match.group(2))}" target="_blank" rel="noreferrer">'
            f"{match.group(1)}</a>"
        ),
        rendered,
    )
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"__(.+?)__", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"\*(.+?)\*", r"<em>\1</em>", rendered)
    rendered = re.sub(r"_(.+?)_", r"<em>\1</em>", rendered)
    rendered = rendered.replace("\n", "<br />")
    return rendered


def html_block_markdown(value: Any) -> str:
    markdown_text = str(value or "").replace("\r\n", "\n")
    if not markdown_text.strip():
        return ""

    lines = markdown_text.split("\n")
    output: list[str] = []
    paragraph: list[str] = []
    current_list_type: str | None = None
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if not paragraph:
            return
        output.append(f"<p>{html_inline_markdown(chr(10).join(paragraph))}</p>")
        paragraph = []

    def flush_list() -> None:
        nonlocal current_list_type, list_items
        if not list_items:
            return
        tag = "ol" if current_list_type == "ol" else "ul"
        items_html = "".join(
            f"<li>{html_inline_markdown(item)}</li>" for item in list_items
        )
        output.append(f"<{tag}>{items_html}</{tag}>")
        current_list_type = None
        list_items = []

    for raw_line in lines:
        line = raw_line.rstrip()
        unordered_match = re.match(r"^\s*[-*+]\s+(.*)$", line)
        ordered_match = re.match(r"^\s*\d+\.\s+(.*)$", line)

        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        if unordered_match:
            flush_paragraph()
            if current_list_type and current_list_type != "ul":
                flush_list()
            current_list_type = "ul"
            list_items.append(unordered_match.group(1))
            continue

        if ordered_match:
            flush_paragraph()
            if current_list_type and current_list_type != "ol":
                flush_list()
            current_list_type = "ol"
            list_items.append(ordered_match.group(1))
            continue

        flush_list()
        paragraph.append(line)

    flush_paragraph()
    flush_list()
    return "".join(output)


def section_shows_time_span(section_name: str | None, design: Any) -> bool:
    if not section_name:
        return False

    snake_case = re.sub(r"[^a-zA-Z0-9]+", "_", section_name).strip("_").lower()
    show_time_spans_in = getattr(getattr(design, "sections", None), "show_time_spans_in", [])
    return snake_case in show_time_spans_in


def render_entry_field(
    entry: Any,
    design: Any,
    locale: Any,
    settings: Any,
    field_name: str,
    section_name: str | None = None,
) -> str:
    from rendercv.renderer.templater.entry_templates_from_input import render_entry_templates
    from rendercv.renderer.templater.string_processor import make_keywords_bold

    if isinstance(entry, str) or not hasattr(entry, "entry_type_in_snake_case"):
        return ""

    entry_copy = entry.model_copy(deep=True) if hasattr(entry, "model_copy") else copy.deepcopy(entry)
    entry_copy = render_entry_templates(
        entry_copy,
        templates=design.templates,
        locale=locale,
        show_time_span=section_shows_time_span(section_name, design),
        current_date=settings._resolved_current_date,
    )
    value = getattr(entry_copy, field_name, "")
    if value is None:
        return ""
    return make_keywords_bold(str(value), settings.bold_keywords)


def parse_entry_blocks(
    entry: Any,
    design: Any,
    locale: Any,
    settings: Any,
    field_name: str,
    section_name: str | None = None,
    file_type: str = "html",
) -> list[dict[str, Any]]:
    from rendercv.renderer.templater.markdown_parser import markdown_to_typst

    blocks = parse_styled_blocks(
        render_entry_field(entry, design, locale, settings, field_name, section_name),
        design,
    )
    if file_type != "typst":
        return blocks

    processed_blocks: list[dict[str, Any]] = []
    for block in blocks:
        block_copy = copy.deepcopy(block)
        if block_copy["type"] == "line":
            for segment in block_copy["segments"]:
                segment["text"] = markdown_to_typst(segment["text"])
            block_copy["text"] = "".join(segment["text"] for segment in block_copy["segments"])
        else:
            block_copy["text"] = markdown_to_typst(block_copy["text"])
        processed_blocks.append(block_copy)

    return processed_blocks
