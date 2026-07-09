from __future__ import annotations

import functools
import re
from collections.abc import Callable
from typing import Literal

from rendercv.renderer.templater import templater

from .template_helpers import (
    body_is_in_main_column,
    count_header_lines,
    entry_date_template,
    entry_main_template,
    html_style,
    html_block_markdown,
    html_inline_markdown,
    parse_entry_blocks,
    parse_styled_blocks,
    render_entry_field,
    remaining_blocks,
    section_shows_time_span,
    typst_text_options,
)


_MARKDOWN_PROTECTED_PATTERN = re.compile(
    r"(\[[^\]]*?\]\{[^{}]+\}|\*\*.*?\*\*|\*.*?\*)",
    re.DOTALL,
)
_BODY_FIELD_NAMES = {
    "summary",
    "highlights",
    "details",
    "description",
    "responsibilities",
    "achievements",
    "bullets",
}


def _install_safe_keyword_bolding() -> None:
    import rendercv.renderer.templater.model_processor as model_processor
    import rendercv.renderer.templater.string_processor as string_processor

    if getattr(string_processor.make_keywords_bold, "_cv_safe_keywords", False):
        return

    original_make_keywords_bold = string_processor.make_keywords_bold

    def safe_make_keywords_bold(string: str, keywords: list[str]) -> str:
        if not keywords:
            return string

        parts = _MARKDOWN_PROTECTED_PATTERN.split(string)
        protected = {
            part
            for part in parts
            if part and _MARKDOWN_PROTECTED_PATTERN.fullmatch(part)
        }
        processed_parts = [
            part if part in protected else original_make_keywords_bold(part, keywords)
            for part in parts
        ]
        return "".join(processed_parts)

    safe_make_keywords_bold._cv_safe_keywords = True  # type: ignore[attr-defined]
    string_processor.make_keywords_bold = safe_make_keywords_bold
    model_processor.make_keywords_bold = safe_make_keywords_bold


def _install_selective_keyword_bolding() -> None:
    import rendercv.renderer.templater.model_processor as model_processor
    import rendercv.renderer.templater.string_processor as string_processor
    from rendercv.renderer.templater.date import build_date_placeholders, date_object_to_string
    from rendercv.renderer.templater.entry_templates_from_input import render_entry_templates
    from rendercv.renderer.templater.footer_and_top_note import (
        render_footer_template,
        render_top_note_template,
    )
    from rendercv.renderer.templater.markdown_parser import markdown_to_typst
    from rendercv.renderer.templater.connections import compute_connections

    if getattr(model_processor.process_model, "_cv_selective_keywords", False):
        return

    def apply_keywords_to_body_fields(entry, keywords: list[str]):
        if isinstance(entry, str) or not keywords:
            return entry

        data = entry.model_dump(exclude_none=True)
        for field, value in data.items():
            if field.startswith("_") or field not in _BODY_FIELD_NAMES:
                continue

            if isinstance(value, str):
                setattr(entry, field, string_processor.make_keywords_bold(value, keywords))
            elif isinstance(value, list):
                setattr(
                    entry,
                    field,
                    [
                        string_processor.make_keywords_bold(item, keywords)
                        if isinstance(item, str)
                        else item
                        for item in value
                    ],
                )

        return entry

    def process_model_with_selective_keywords(rendercv_model, file_type: Literal["typst", "markdown"]):
        rendercv_model = rendercv_model.model_copy(deep=True)

        string_processors: list[Callable[[str], str]] = []
        if file_type == "typst":
            string_processors.append(markdown_to_typst)

        rendercv_model.cv._plain_name = rendercv_model.cv.name
        rendercv_model.cv.name = model_processor.apply_string_processors(
            rendercv_model.cv.name, string_processors
        )
        rendercv_model.cv.headline = model_processor.apply_string_processors(
            rendercv_model.cv.headline, string_processors
        )
        rendercv_model.cv._connections = compute_connections(rendercv_model, file_type)
        rendercv_model.cv._top_note = render_top_note_template(
            rendercv_model.design.templates.top_note,
            locale=rendercv_model.locale,
            current_date=rendercv_model.settings._resolved_current_date,
            name=rendercv_model.cv.name,
            single_date_template=rendercv_model.design.templates.single_date,
            string_processors=string_processors,
        )

        rendercv_model.cv._footer = render_footer_template(
            rendercv_model.design.templates.footer,
            locale=rendercv_model.locale,
            current_date=rendercv_model.settings._resolved_current_date,
            name=rendercv_model.cv.name,
            single_date_template=rendercv_model.design.templates.single_date,
            string_processors=string_processors,
        )

        pdf_title_placeholders: dict[str, str] = {
            "CURRENT_DATE": date_object_to_string(
                rendercv_model.settings._resolved_current_date,
                locale=rendercv_model.locale,
                single_date_template=rendercv_model.design.templates.single_date,
            ),
            "NAME": rendercv_model.cv._plain_name or "",
            **build_date_placeholders(
                rendercv_model.settings._resolved_current_date,
                locale=rendercv_model.locale,
            ),
        }
        rendercv_model.settings.pdf_title = model_processor.substitute_placeholders(
            rendercv_model.settings.pdf_title, pdf_title_placeholders
        )

        if rendercv_model.cv.sections is None:
            return rendercv_model

        for section in rendercv_model.cv.rendercv_sections:
            section.title = model_processor.apply_string_processors(
                section.title, string_processors
            )
            show_time_span = (
                section.snake_case_title
                in rendercv_model.design.sections.show_time_spans_in
            )
            for i, entry in enumerate(section.entries):
                entry = apply_keywords_to_body_fields(
                    entry,
                    rendercv_model.settings.bold_keywords,
                )
                entry = render_entry_templates(
                    entry,
                    templates=rendercv_model.design.templates,
                    locale=rendercv_model.locale,
                    show_time_span=show_time_span,
                    current_date=rendercv_model.settings._resolved_current_date,
                )
                section.entries[i] = model_processor.process_fields(entry, string_processors)

        return rendercv_model

    process_model_with_selective_keywords._cv_selective_keywords = True  # type: ignore[attr-defined]
    model_processor.process_model = process_model_with_selective_keywords
    templater.process_model = process_model_with_selective_keywords


def install() -> None:
    _install_safe_keyword_bolding()
    _install_selective_keyword_bolding()
    current = templater.get_jinja2_environment
    if getattr(current, "_cv_helpers_installed", False):
        return

    original = getattr(current, "__wrapped__", current)

    @functools.lru_cache(maxsize=1)
    def get_jinja2_environment_with_cv_helpers(input_file_path=None):
        env = original(input_file_path)
        env.globals["cv_parse_styled_blocks"] = parse_styled_blocks
        env.globals["cv_count_header_lines"] = count_header_lines
        env.globals["cv_entry_main_template"] = entry_main_template
        env.globals["cv_entry_date_template"] = entry_date_template
        env.globals["cv_parse_entry_blocks"] = parse_entry_blocks
        env.globals["cv_render_entry_field"] = render_entry_field
        env.globals["cv_body_is_in_main_column"] = body_is_in_main_column
        env.globals["cv_remaining_blocks"] = remaining_blocks
        env.globals["cv_section_shows_time_span"] = section_shows_time_span
        env.globals["cv_typst_text_options"] = typst_text_options
        env.globals["cv_html_style"] = html_style
        env.globals["cv_html_block_markdown"] = html_block_markdown
        env.globals["cv_html_inline_markdown"] = html_inline_markdown
        return env

    get_jinja2_environment_with_cv_helpers._cv_helpers_installed = True  # type: ignore[attr-defined]
    templater.get_jinja2_environment = get_jinja2_environment_with_cv_helpers

    if not getattr(templater.render_full_template, "_cv_last_entry_installed", False):
        original_render_full_template = templater.render_full_template

        def render_full_template_with_last_entry(rendercv_model, file_type):
            extension = {
                "typst": "typ",
                "markdown": "md",
            }[file_type]

            from rendercv.renderer.templater.model_processor import (
                download_photo_from_url,
                process_model,
            )

            download_photo_from_url(rendercv_model)
            rendercv_model = process_model(rendercv_model, file_type)

            header = templater.render_single_template(
                file_type,
                f"Header.j2.{extension}",
                rendercv_model,
            )
            if file_type == "typst":
                preamble = templater.render_single_template(
                    file_type,
                    f"Preamble.j2.{extension}",
                    rendercv_model,
                )
                code = f"{preamble}\n\n{header}\n"
            else:
                code = f"{header}\n"

            for rendercv_section in rendercv_model.cv.rendercv_sections:
                section_beginning = templater.render_single_template(
                    file_type,
                    f"SectionBeginning.j2.{extension}",
                    rendercv_model,
                    section_title=rendercv_section.title,
                    snake_case_section_title=rendercv_section.snake_case_title,
                    entry_type=rendercv_section.entry_type,
                )
                section_ending = templater.render_single_template(
                    file_type,
                    f"SectionEnding.j2.{extension}",
                    rendercv_model,
                    entry_type=rendercv_section.entry_type,
                )
                entry_codes = []
                entry_count = len(rendercv_section.entries)
                for index, entry in enumerate(rendercv_section.entries):
                    entry_code = templater.render_single_template(
                        file_type,
                        f"entries/{rendercv_section.entry_type}.j2.{extension}",
                        rendercv_model,
                        entry=entry,
                        is_last_entry=index == entry_count - 1,
                    )
                    entry_codes.append(entry_code)
                entries_code = "\n\n".join(entry_codes)
                section_code = f"{section_beginning}\n{entries_code}\n{section_ending}"
                code += f"\n{section_code}"

            return code

        render_full_template_with_last_entry._cv_last_entry_installed = True  # type: ignore[attr-defined]
        templater.render_full_template = render_full_template_with_last_entry
