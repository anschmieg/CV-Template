from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import anschmiegcv
import cv


class PackageBoundaryTests(unittest.TestCase):
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
