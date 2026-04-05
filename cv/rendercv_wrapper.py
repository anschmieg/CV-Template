from __future__ import annotations

import sys
from pathlib import Path

from .google_fonts import ensure_google_fonts_cached
from .jinja_hooks import install


def _extract_render_paths(argv: list[str]) -> tuple[Path | None, Path | None]:
    if len(argv) < 2 or argv[1] != "render":
        return None, None

    input_path: Path | None = None
    design_path: Path | None = None
    index = 2
    while index < len(argv):
        argument = argv[index]
        if argument in {"-h", "--help"}:
            return None, None
        if argument == "--design" and index + 1 < len(argv):
            design_path = Path(argv[index + 1]).resolve()
            index += 2
            continue
        if argument.startswith("--"):
            index += 1
            continue
        if input_path is None:
            input_path = Path(argument).resolve()
        index += 1

    return input_path, design_path


def main() -> None:
    input_path, design_path = _extract_render_paths(sys.argv)
    if input_path is not None:
        ensure_google_fonts_cached(input_path, design_path)

    install()

    from rendercv.cli.entry_point import entry_point

    entry_point()


if __name__ == "__main__":
    main()
