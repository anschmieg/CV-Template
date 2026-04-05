from __future__ import annotations

from .jinja_hooks import install


def main() -> None:
    install()

    from rendercv.cli.entry_point import entry_point

    entry_point()


if __name__ == "__main__":
    main()
