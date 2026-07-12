from __future__ import annotations

import unittest
from types import SimpleNamespace

from cv.template_helpers import (
    entry_supports_timeline,
    card_content_score,
    card_grid_span,
    card_layout_request,
    parse_styled_blocks,
    resolve_card_layout,
)


class TemplateHelperTests(unittest.TestCase):
    def test_only_rendercv_experience_and_education_entries_support_timeline(self) -> None:
        self.assertTrue(entry_supports_timeline(SimpleNamespace(entry_type_in_snake_case="experience_entry")))
        self.assertTrue(entry_supports_timeline(SimpleNamespace(entry_type_in_snake_case="education_entry")))
        self.assertFalse(entry_supports_timeline(SimpleNamespace(entry_type_in_snake_case="normal_entry")))
        self.assertFalse(entry_supports_timeline(SimpleNamespace(entry_type_in_snake_case="publication_entry")))
        self.assertFalse(entry_supports_timeline("plain text"))

    def test_parse_styled_blocks_ignores_unresolved_field_markers(self) -> None:
        blocks = parse_styled_blocks(
            "**Certificate**\n!!! summary\n*voraussichtlicher Abschluss*",
            design=None,
        )

        self.assertEqual([block["text"] for block in blocks], ["**Certificate**", "*voraussichtlicher Abschluss*"])

    def test_styled_span_accepts_nested_rendered_emphasis(self) -> None:
        blocks = parse_styled_blocks(
            "[#emph[SCHULWÄRTS!] Stipendiatin, ]{.semibold}[Goethe-Institut]{.medium}",
            design=None,
        )

        self.assertEqual(
            [segment["text"] for segment in blocks[0]["segments"]],
            ["#emph[SCHULWÄRTS!] Stipendiatin, ", "Goethe-Institut"],
        )
        self.assertEqual(
            [segment["style"]["weight"] for segment in blocks[0]["segments"]],
            ["600", "500"],
        )

    def test_card_layout_keeps_three_short_entries_on_one_row(self) -> None:
        entries = [
            {"label": "Deutsch", "details": "Erstsprache"},
            {"label": "Englisch", "details": "C1"},
            {"label": "Spanisch", "details": "B2"},
        ]

        self.assertEqual(resolve_card_layout(entries), "three")

    def test_card_layout_keeps_two_detailed_entries_equal(self) -> None:
        entries = [
            {"name": "Certificate", "highlights": ["A detailed point", "Another detailed point"]},
            {"name": "Training", "highlights": ["One", "Two", "Three", "Four"]},
        ]

        self.assertEqual(resolve_card_layout(entries), "two")

    def test_explicit_card_layout_suffix_stays_authoritative(self) -> None:
        self.assertEqual(card_layout_request("Skills {.cards-3}"), "three")
        self.assertEqual(resolve_card_layout([{"label": "Only"}], "three"), "three")

    def test_dynamic_grid_promotes_content_heavy_cards(self) -> None:
        entry = {
            "name": "Advanced qualification",
            "summary": "A substantial summary explaining the qualification in detail.",
            "highlights": ["A detailed highlight"] * 6,
        }
        entries = [entry] + [
            {"label": f"Skill {index}", "details": "Advanced"} for index in range(4)
        ]

        score = card_content_score(entry)
        self.assertGreaterEqual(score, 7.5)
        self.assertEqual(resolve_card_layout(entries), "dynamic")
        self.assertEqual(card_grid_span(score, "dynamic"), (2, 2))


if __name__ == "__main__":
    unittest.main()
