from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from cv import cli


class CliTests(unittest.TestCase):
    def test_bare_command_renders_discovered_default_input(self) -> None:
        discovered = Path("julia_data.yaml")

        with (
            patch.object(cli, "discover_default_input", return_value=discovered) as discover,
            patch.object(cli, "render_cv") as render_cv,
        ):
            self.assertEqual(cli.main([]), 0)

        discover.assert_called_once_with(Path.cwd())
        render_cv.assert_called_once_with(discovered, extra_rendercv_args=[])

    def test_render_command_without_input_renders_discovered_default_input(self) -> None:
        discovered = Path("julia_data.yaml")

        with (
            patch.object(cli, "discover_default_input", return_value=discovered),
            patch.object(cli, "render_cv") as render_cv,
        ):
            self.assertEqual(cli.main(["render"]), 0)

        render_cv.assert_called_once_with(discovered, extra_rendercv_args=[])

    def test_bare_command_forwards_rendercv_options(self) -> None:
        discovered = Path("julia_data.yaml")

        with (
            patch.object(cli, "discover_default_input", return_value=discovered),
            patch.object(cli, "render_cv") as render_cv,
        ):
            self.assertEqual(cli.main(["--dont-generate-pdf"]), 0)

        render_cv.assert_called_once_with(
            discovered,
            extra_rendercv_args=["--dont-generate-pdf"],
        )

    def test_merge_command_still_writes_merged_yaml(self) -> None:
        output = Path("julia.rendercv.yaml")

        with patch.object(cli, "merge_to_file", return_value=output) as merge_to_file:
            printer = Mock()
            self.assertEqual(cli.main(["merge", "julia_data.yaml"], print_fn=printer), 0)

        merge_to_file.assert_called_once_with(Path("julia_data.yaml"), output_path=None)
        printer.assert_called_once_with(output)


if __name__ == "__main__":
    unittest.main()
