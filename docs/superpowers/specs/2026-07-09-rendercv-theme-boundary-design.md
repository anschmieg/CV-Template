# RenderCV Theme Boundary Design

## Goal

Keep this repository a thin RenderCV extension by making the boundary explicit:
`cv` is the concise helper command, and `anschmiegcv` is the unambiguous RenderCV
theme identity.

## Current State

The project already uses RenderCV 2.8, which is the latest PyPI release as of
2026-07-09. `pyproject.toml` allows `rendercv>=2.8`, and `uv.lock` resolves
RenderCV to `2.8`.

The architectural issue is package ownership. Theme templates and the theme
model are currently implemented under `cv/`, while `anschmiegcv/` mostly aliases
or mirrors that implementation. The CLI is also in `cv/`, so the helper layer
and theme layer are mixed.

## Design

The project should expose two clear surfaces:

- `uv run cv`: the concise user command. With no arguments it renders the
  default detected CV input. Subcommands such as `render` and `merge` remain
  available for explicit use.
- `anschmiegcv`: the RenderCV theme name and package. YAML uses
  `design.theme: anschmiegcv`, and RenderCV template lookup should resolve the
  theme through this package directly.

Package responsibilities:

- `anschmiegcv/`: theme model, theme-specific schema extensions, Typst
  templates, and any theme-owned template helpers needed by RenderCV.
- `cv/`: helper CLI, input discovery, split data/design pairing, merge
  inspection, font caching convenience, and forwarding to native RenderCV.
- `cv_tools/`: compatibility shim only.

## Behavior

`uv run cv` should behave like `uv run cv render`.

`uv run cv render` should keep the existing split-input behavior:

- choose a single default `*_data.yaml` when unambiguous
- pair it with a matching `*_design.yaml`
- forward rendering to native RenderCV with `--design`
- leave all unknown options to RenderCV

The compatibility script name `anschmiegcv` may continue to exist, but docs
should describe it as a compatibility alias rather than the preferred command.

## Dependency Policy

Keep RenderCV native behavior as the source of truth. The project should depend
on the latest confirmed RenderCV major line, using `rendercv>=2.8,<3` so future
minor releases are accepted while an unreviewed major version is not installed
silently.

## Validation

Validation should cover:

- helper behavior with direct unit tests for default command handling and
  split-input forwarding
- package import boundaries for `cv` and `anschmiegcv`
- rendering through `uv run cv` for HTML and PDF/Typst output when practical

