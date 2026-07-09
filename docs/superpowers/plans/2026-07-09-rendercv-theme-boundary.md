# RenderCV Theme Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `cv` the concise helper command and `anschmiegcv` the clear RenderCV theme owner.

**Architecture:** Move theme-owned Python model code and package data declarations to `anschmiegcv`, leave helper orchestration in `cv`, and make bare `uv run cv` default to rendering. Keep RenderCV as the rendering authority.

**Tech Stack:** Python 3.12+, RenderCV 2.8, setuptools, uv, PyYAML, unittest/pytest-compatible tests.

---

### Task 1: Add CLI Behavior Tests

**Files:**
- Create: `tests/test_cli.py`
- Modify: `cv/cli.py`

- [x] Write tests proving that `main([])` renders the discovered default input, `main(["render"])` does the same, and `main(["merge", "x_data.yaml"])` still calls merge.
- [x] Run the tests and confirm the bare-command test fails before implementation.
- [x] Update `cv.cli.main` to accept an optional argv list and default no command to `render`.
- [x] Re-run the tests and confirm they pass.

### Task 2: Move Theme Ownership

**Files:**
- Modify: `anschmiegcv/__init__.py`
- Modify: `cv/__init__.py`
- Modify: `pyproject.toml`
- Modify: `cv/jinja_hooks.py`

- [x] Move the `Colors` and `CvTheme` implementation from `cv/__init__.py` into `anschmiegcv/__init__.py`, renaming the class to `AnschmiegcvTheme`.
- [x] Leave `cv/__init__.py` as a compatibility import surface only.
- [x] Update `pyproject.toml` package discovery and package data so `anschmiegcv` owns `*.typ` and `entries/*.typ`.
- [x] Remove the `anschmiegcv` to `cv` template fallback from `cv/jinja_hooks.py` once package data is owned by `anschmiegcv`.

### Task 3: Update Docs and Dependency Policy

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `docs/USER_GUIDE.md`

- [x] Change the RenderCV dependency to `rendercv>=2.8,<3`.
- [x] Document `uv run cv` as the preferred command.
- [x] Document `anschmiegcv` as the RenderCV theme identity and compatibility command alias.
- [x] Remove wording that says `cv/` implements the theme.

### Task 4: Validate

**Files:**
- Test: `tests/test_cli.py`

- [x] Run the focused tests.
- [x] Run `uv run cv --dont-generate-pdf --dont-generate-png --dont-generate-markdown` to verify the concise command reaches RenderCV.
- [x] Run `uv run cv render --dont-generate-pdf --dont-generate-png --dont-generate-markdown` to verify the explicit command remains valid.
- [x] Run a full RenderCV render when local dependencies and font cache permissions allow it.
