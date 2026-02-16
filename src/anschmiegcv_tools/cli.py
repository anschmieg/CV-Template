from __future__ import annotations

import argparse
from pathlib import Path

from .palette import build_semantic_palette, list_supported_formats
from .render import render_yaml_files
from .sync import sync_assets


def _add_subcommands(parser: argparse.ArgumentParser) -> None:
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Sync shared assets into a repo")
    sync_parser.add_argument("--target", default=".", help="Repository root where assets are synced")

    palette_parser = subparsers.add_parser("palette", help="Generate semantic palette from seed color")
    palette_parser.add_argument("seed", help="Primary color seed (#RRGGBB, rgb(...), hsl(...))")
    palette_parser.add_argument("--accent-seed", help="Optional secondary accent seed")

    render_parser = subparsers.add_parser("render", help="Render YAML files via RenderCV with palette preprocessing")
    render_parser.add_argument("files", nargs="*", help="Input YAML files; default *_CV.yaml")
    render_parser.add_argument("--cwd", default=".", help="Working directory for file discovery/sync")
    render_parser.add_argument("--no-sync", action="store_true", help="Skip syncing assets before rendering")
    render_parser.add_argument(
        "--keyword-highlight",
        action="store_true",
        help="Apply optional keyword semibold markup based on settings.bold_keywords",
    )


def main() -> int:
    parser = argparse.ArgumentParser(prog="anschmiegcv")
    _add_subcommands(parser)
    args, unknown = parser.parse_known_args()

    if args.command == "sync":
        changed = sync_assets(Path(args.target))
        print(f"Synced {len(changed)} file(s)")
        for path in changed:
            print(f" - {path}")
        return 0

    if args.command == "palette":
        palette = build_semantic_palette(args.seed, accent_seed=args.accent_seed)
        for key, value in palette.items():
            print(f"{key}: {value}")
        print("supported_input_formats:")
        for fmt in list_supported_formats():
            print(f" - {fmt}")
        return 0

    if args.command == "render":
        render_yaml_files(
            [Path(p) for p in args.files],
            cwd=Path(args.cwd).resolve(),
            sync_before_render=not args.no_sync,
            enable_keyword_highlight=args.keyword_highlight,
            extra_rendercv_args=unknown,
        )
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
