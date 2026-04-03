# CV-Template

This repo now centers on two things:

- the local `anschmiegcv` RenderCV theme
- a very small `cv` CLI wrapper that detects split YAML inputs and forwards them to RenderCV

## Layout

- `cv/`: the Python package that implements the `anschmiegcv` RenderCV theme
- `cv/`: also contains the tiny helper modules for `merge` and `render`
- `example_data.yaml`: sample CV data, plus `settings` and optional `locale`
- `example_design.yaml`: sample `design` overlay

## Usage

Install the project in editable mode, or run it from this repo with `uv`.

### Recommended naming

- `*_data.yaml`: main RenderCV input containing `cv`, plus optional `settings` and `locale`
- `*_design.yaml`: companion file containing only the top-level `design:` block

This avoids colliding with RenderCV’s common merged-file naming like `Name_CV.yaml`.

### Render split inputs automatically

```bash
uv run cv render example_data.yaml
```

If `example_design.yaml` exists next to it, the wrapper calls RenderCV with the native `--design` overlay.

If there is exactly one `*_data.yaml` in the current directory, you can omit the filename:

```bash
uv run cv render
```

You can also point `render` at either companion file:

```bash
uv run cv render example_design.yaml
```

### Render without `uv`

There is also a tiny repo-local runner:

```bash
./render
```

Or, if you prefer invoking Python directly:

```bash
python render
```

It prefers the project `.venv` when present, and otherwise falls back to the current Python.

### Merge split inputs into one file

```bash
uv run cv merge example_data.yaml
```

That writes `example.rendercv.yaml` by default.

For compatibility, `uv run anschmiegcv ...` still works too.

## Theme notes

- The Python package names are `cv` and `cv_tools`, but the RenderCV theme name is `anschmiegcv`.
- PDF and HTML now share the same fallback semantics: when a template span does not specify a class like `.color-headline` or `.w600`, custom entry rendering falls back to RenderCV-native design tokens from `design.colors`, `design.typography`, `design.entries`, and `design.sections` rather than separate hardcoded theme values.
- Section title directives like `{.cards}` and `{.timeline}` are handled by the theme templates.
- Theme-specific colors `timeline_dot` and `timeline_line` are supported through `cv/__init__.py`.
- `design.colors` supports two modes:
  - explicit RenderCV-native element colors such as `body`, `headline`, `section_titles`, `timeline_dot`, and `timeline_line`
  - optional palette generation via `accent` and optional `base`, which fills any missing RenderCV-native color tokens while still letting explicit per-element colors override the generated values
- Entry templates now drive both PDF and HTML consistently.
- HTML timeline geometry is derived from the same design values mathematically, using exact `calc()` relationships rather than visual nudges.
- Markdown in template lines is respected in both outputs, for example:

  ```yaml
  design:
    templates:
      education_entry:
        main_column: |
          **AREA**, DEGREE
          INSTITUTION
          HIGHLIGHTS
  ```

- Preferred styling syntax is Pandoc-style spans with classes:

  ```yaml
  design:
    templates:
      education_entry:
        main_column: |
          [AREA]{.color-section_titles .semibold}, [DEGREE]{.color-black .regular}
          [INSTITUTION]{.color-headline .italic}
          HIGHLIGHTS
  ```

- Supported span classes include:
  - `.color-headline`, `.color-section_titles`, `.color-footer`, etc. for any key in `design.colors`
  - `.color-red`, `.color-black`, or other literal color names if they are valid in HTML/Typst
  - `.weight-400`, `.weight-500`, `.weight-600`, `.weight-700`
  - shorthand `.w400`, `.w500`, `.w600`, `.w700`
  - built-ins like `.regular`, `.medium`, `.semibold`, `.bold`, `.italic`, and `.underline`
- Classes can be combined on one span, and mid-line styling works naturally:

  ```yaml
  main_column: |
    [AREA]{.color-section_titles .w600}, [DEGREE]{.color-black .weight-400}
  ```

- Legacy `{color:...}` inline directives still work, but span classes are the recommended syntax going forward.

### Color configuration modes

You can either set every RenderCV color token directly:

```yaml
design:
  colors:
    body: rgb(25, 48, 51)
    name: rgb(0, 120, 135)
    headline: rgb(3, 103, 116)
    section_titles: rgb(0, 50, 108)
    timeline_dot: rgb(0, 50, 108)
    timeline_line: rgb(0, 50, 108)
```

Or you can provide a palette seed and let `anschmiegcv` derive any missing tokens:

```yaml
design:
  colors:
    accent: "#007887"
    base: "#222222"
```

In palette mode:

- `accent` drives the heading, link, and timeline family
- `base` drives the body / neutral family
- any explicitly provided RenderCV-native token still wins over the generated palette
- PDF and HTML both consume the resolved `design.colors.*` values, so they stay in sync

## Screenshots

![Screenshot - Desktop 1](pics/screenshots/desktop-1.png)
![Screenshot - Desktop 2](pics/screenshots/desktop-2.png)
