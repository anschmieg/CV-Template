from __future__ import annotations

import argparse
from pathlib import Path

from .merge import discover_default_input, merge_to_file, render_cv


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cv")
    subparsers = parser.add_subparsers(dest="command", required=True)

    merge_parser = subparsers.add_parser(
        "merge",
        help="Merge split RenderCV inputs into one YAML file for inspection or export",
    )
    merge_parser.add_argument("input_file", help="Path to a merged YAML, *_data.yaml, or *_design.yaml")
    merge_parser.add_argument(
        "--output",
        help="Where to write the merged YAML (defaults to <base>.rendercv.yaml)",
    )

    render_parser = subparsers.add_parser(
        "render",
        help="Render a merged YAML directly, or auto-detect a *_data + *_design companion pair",
    )
    render_parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to a merged YAML, *_data.yaml, or *_design.yaml",
    )

    return parser


def main() -> int:
    parser = _build_parser()
    args, unknown = parser.parse_known_args()

    output_path = Path(args.output) if getattr(args, "output", None) else None

    if args.command == "merge":
        input_path = Path(args.input_file)
        merged_path = merge_to_file(input_path, output_path=output_path)
        print(merged_path)
        return 0

    if args.command == "render":
        input_value = args.input_file or str(discover_default_input(Path.cwd()))
        input_path = Path(input_value)
        render_cv(input_path, extra_rendercv_args=unknown)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
