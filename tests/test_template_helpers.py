from __future__ import annotations

import unittest

from cv.template_helpers import parse_styled_blocks


class TemplateHelperTests(unittest.TestCase):
    def test_parse_styled_blocks_ignores_unresolved_field_markers(self) -> None:
        blocks = parse_styled_blocks(
            "**Certificate**\n!!! summary\n*voraussichtlicher Abschluss*",
            design=None,
        )

        self.assertEqual([block["text"] for block in blocks], ["**Certificate**", "*voraussichtlicher Abschluss*"])


if __name__ == "__main__":
    unittest.main()
