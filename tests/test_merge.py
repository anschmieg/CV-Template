from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from cv.merge import resolve_inputs


class ResolveInputsTests(unittest.TestCase):
    def test_shared_design_is_used_for_multiple_data_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            shared_design = directory / "design.yaml"
            shared_design.touch()

            for language in ("en", "de"):
                data_path = directory / f"{language}_data.yaml"
                data_path.touch()
                self.assertEqual(
                    resolve_inputs(data_path).design_path,
                    shared_design.resolve(),
                )

    def test_stem_specific_design_takes_precedence_over_shared_design(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            data_path = directory / "en_data.yaml"
            stem_design = directory / "en_design.yaml"
            data_path.touch()
            stem_design.touch()
            (directory / "design.yaml").touch()

            self.assertEqual(
                resolve_inputs(data_path).design_path, stem_design.resolve()
            )

    def test_shared_design_name_is_supported_as_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            data_path = directory / "en_data.yml"
            shared_design = directory / "shared_design.yml"
            data_path.touch()
            shared_design.touch()

            self.assertEqual(
                resolve_inputs(data_path).design_path, shared_design.resolve()
            )


if __name__ == "__main__":
    unittest.main()
