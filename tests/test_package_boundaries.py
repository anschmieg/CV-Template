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


if __name__ == "__main__":
    unittest.main()
