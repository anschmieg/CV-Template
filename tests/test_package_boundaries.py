from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import anschmiegcv
import cv


class PackageBoundaryTests(unittest.TestCase):
    def test_card_sections_skip_content_area_before_accumulating_entries(self) -> None:
        template = Path("anschmiegcv/SectionBeginning.j2.typ").read_text()

        marker_index = template.index('#metadata("skip-content-area")')
        clear_index = template.index("#anschmiegcv_cards_clear()")

        self.assertLess(marker_index, clear_index)

    def test_list_sections_use_full_width_and_headings_use_reduced_gutter(self) -> None:
        section_template = Path("anschmiegcv/SectionBeginning.j2.typ").read_text()
        preamble = Path("anschmiegcv/Preamble.j2.typ").read_text()

        self.assertIn('{% elif view_mode in ["cards", "list"] %}', section_template)
        self.assertIn('#metadata("skip-content-area")', section_template)
        one_line_template = Path("anschmiegcv/entries/OneLineEntry.j2.typ").read_text()
        self.assertIn(
            'anschmiegcv_section_view_mode == "list"', one_line_template
        )
        self.assertIn(
            "below: {{ design.typography.line_spacing }}",
            one_line_template,
        )
        self.assertIn(
            "spacing: {{ design.typography.line_spacing }}",
            preamble,
        )
        self.assertIn(
            "{{ design.entries.date_and_location_width }} + "
            "{{ design.entries.side_space }}",
            preamble,
        )
        self.assertIn(") * 0.5", preamble)

    def test_timeline_typography_uses_measured_alignment_and_body_spacing(self) -> None:
        preamble = Path("anschmiegcv/Preamble.j2.typ").read_text()
        html = Path("html/Full.html").read_text()
        self.assertNotIn("primary-to-organization-gap", preamble)

        for template_name in ("ExperienceEntry.j2.typ", "EducationEntry.j2.typ"):
            template = Path("anschmiegcv/entries", template_name).read_text()
            self.assertIn(
                "{% set has_body_blocks = main_blocks|length > header_count %}",
                template,
            )
            self.assertIn(
                "top: {{ design.typography.line_spacing }} * 0.8", template
            )
            self.assertIn(
                "bottom: {{ design.typography.line_spacing }} * "
                "{% if has_body_blocks %}1.3{% else %}0.8{% endif %}",
                template,
            )
            self.assertIn("#text(size: 0.92em)[", template)
        self.assertIn(
            "body-cap-height - metadata-font-size",
            preamble,
        )
        self.assertNotIn("metadata-cap-height", preamble)
        self.assertIn(".cv-timeline-content .cv-highlights", html)
        self.assertIn("font-size: 92%;", html)
        self.assertIn("margin-top: 0.3rem !important;", html)

    def test_theme_defaults_use_two_line_timeline_headers(self) -> None:
        theme = anschmiegcv.AnschmiegcvTheme()

        self.assertEqual(
            theme.templates.education_entry.main_column.splitlines()[:2],
            [
                "[AREA]{.color-section_titles .bold} [DEGREE]{.color-section_titles .semibold}",
                "[INSTITUTION]{.color-body .semibold}",
            ],
        )
        self.assertIsNone(theme.templates.education_entry.degree_column)
        self.assertEqual(
            theme.templates.experience_entry.main_column.splitlines()[:2],
            [
                "[POSITION]{.color-section_titles .bold}",
                "[COMPANY]{.color-body .semibold}",
            ],
        )

    def test_anschmiegcv_owns_theme_class(self) -> None:
        self.assertEqual(anschmiegcv.AnschmiegcvTheme().theme, "anschmiegcv")

    def test_cv_reexports_theme_class_for_compatibility(self) -> None:
        self.assertIs(cv.CvTheme, anschmiegcv.AnschmiegcvTheme)

    def test_theme_class_validates_when_loaded_like_rendercv_custom_theme(self) -> None:
        init_path = Path("anschmiegcv/__init__.py").resolve()
        spec = importlib.util.spec_from_file_location("theme", init_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        theme = module.AnschmiegcvTheme(theme="anschmiegcv")

        self.assertEqual(theme.theme, "anschmiegcv")

    def test_accent_seed_generates_missing_palette_tokens(self) -> None:
        theme = anschmiegcv.AnschmiegcvTheme(
            theme="anschmiegcv",
            colors={"accent": "#007887", "base": "#243033"},
        )

        self.assertNotEqual(theme.colors.name.as_rgb(), "rgb(0, 120, 135)")
        self.assertNotEqual(theme.colors.headline.as_rgb(), theme.colors.name.as_rgb())
        self.assertEqual(theme.colors.body.as_rgb(), "rgb(36, 48, 51)")

    def test_explicit_color_tokens_override_accent_palette(self) -> None:
        theme = anschmiegcv.AnschmiegcvTheme(
            theme="anschmiegcv",
            colors={
                "accent": "#007887",
                "base": "#243033",
                "section_titles": "#102030",
            },
        )

        self.assertEqual(theme.colors.section_titles.as_rgb(), "rgb(16, 32, 48)")

    def test_html_options_are_theme_owned(self) -> None:
        theme = anschmiegcv.AnschmiegcvTheme(
            theme="anschmiegcv",
            html={
                "layout": "centered",
                "content_width": "68rem",
                "sidebar_width": "18rem",
                "density": "compact",
                "type_scale": 1.04,
                "motion": False,
            },
        )

        self.assertEqual(theme.html.layout, "centered")
        self.assertEqual(theme.html.content_width, "68rem")
        self.assertEqual(theme.html.density, "compact")
        self.assertFalse(theme.html.motion)


if __name__ == "__main__":
    unittest.main()
