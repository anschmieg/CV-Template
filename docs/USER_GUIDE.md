# User Guide

This repository is a thin layer on top of RenderCV:

- the RenderCV theme name is `anschmiegcv`
- the Python package / CLI names are `cv` and `cv_tools`
- the wrapper only helps with split files and forwards rendering to native RenderCV

## File structure

The recommended input layout is:

- `name_data.yaml`: the main RenderCV input containing `cv`, and optionally `settings` and `locale`
- `name_design.yaml`: a companion file containing only the top-level `design:` block

You can still render a single merged YAML file, but the split layout is the preferred workflow.

## Rendering

From the repo root:

```bash
uv run cv render
```

If there is exactly one `*_data.yaml` file in the current directory, the wrapper auto-detects it and also auto-detects the matching `*_design.yaml`.

If the directory contains sample inputs like `example_data.yaml`, `sample_data.yaml`, or `demo_data.yaml` plus one real non-sample data file, bare `cv render` prefers the non-sample file automatically.

You can also pass a file explicitly:

```bash
uv run cv render example_data.yaml
uv run cv render example_design.yaml
```

The wrapper forwards extra arguments to RenderCV:

```bash
uv run cv render example_data.yaml --pdf-path output/custom.pdf
```

Compatibility alias:

```bash
uv run anschmiegcv render
```

Without `uv`:

```bash
./render
python render
```

By default, `cv render` also uses a convenient font mode:

- HTML loads the configured Google font families directly from Google Fonts
- PDF/PNG caches matching Google `.ttf` files into a local `fonts/` directory beside the YAML inputs when they are missing
- if a font download fails, rendering still proceeds and Typst falls back to other available fonts

## Merge helper

If you want to inspect the fully merged input that RenderCV would receive:

```bash
uv run cv merge example_data.yaml
```

This writes `example.rendercv.yaml` by default.

## Theme customization

All theme customization lives under `design:` in your `*_design.yaml`.

### Standard RenderCV tokens

Use native RenderCV fields wherever possible:

- `design.page`
- `design.colors`
- `design.typography`
- `design.header`
- `design.section_titles`
- `design.sections`
- `design.entries`
- `design.templates`

The theme is designed so PDF and HTML both derive from those same RenderCV-native values.

### Font families

The wrapper reads the unique font families from:

- `design.typography.font_family.body`
- `design.typography.font_family.name`
- `design.typography.font_family.headline`
- `design.typography.font_family.connections`
- `design.typography.font_family.section_titles`

In the default convenient mode:

- HTML uses those families through Google Fonts
- PDF/PNG uses locally cached Google `.ttf` files under `fonts/google/<family-slug>/`

The `fonts/` directory is runtime cache and is ignored by Git.

### Color modes

There are two supported color workflows.

#### 1. Explicit token mode

Set individual RenderCV color tokens directly:

```yaml
design:
  colors:
    body: rgb(25, 48, 51)
    name: rgb(0, 50, 108)
    headline: rgb(0, 50, 108)
    section_titles: rgb(0, 50, 108)
    links: rgb(0, 50, 108)
    connections: rgb(0, 50, 108)
    timeline_dot: rgb(0, 50, 108)
    timeline_line: rgb(0, 50, 108)
```

#### 2. Palette mode

Provide a seed accent and optional base color:

```yaml
design:
  colors:
    accent: "#007887"
    base: "#222222"
```

In palette mode:

- `accent` drives headings, links, and timeline accents
- `base` drives body and neutral text
- explicit tokens still override generated ones

### Entry templates

The theme supports custom `main_column` and `date_and_location_column` templates for entry types like education and experience.

Example:

```yaml
design:
  templates:
    education_entry:
      main_column: |
        [AREA, ]{.color-section_titles .bold}[DEGREE]{.color-body .semibold}
        [INSTITUTION]{.color-body .semibold}
        HIGHLIGHTS
      date_and_location_column: "LOCATION\nDATE"
```

### Inline styling syntax

Preferred syntax is Pandoc-style span classes:

```yaml
main_column: |
  [AREA]{.color-section_titles .w600}, [DEGREE]{.color-body .weight-400}
  [INSTITUTION]{.color-headline .italic}
```

Supported classes include:

- `.color-{token}` for keys under `design.colors`, like `.color-headline`
- `.weight-400`, `.weight-500`, `.weight-600`, `.weight-700`
- shorthand `.w400`, `.w500`, `.w600`, `.w700`
- `.regular`, `.medium`, `.semibold`, `.bold`
- `.italic`, `.underline`

Legacy `{color:...}` directives still work, but the span-class syntax is the recommended path.

## View modes

Section titles can include lightweight directives:

- `{.timeline}` for timeline sections
- `{.cards}` for card layouts
- `{.cards-1}`, `{.cards-2}`, `{.cards-3}`, `{.cards-3w}`, `{.cards-4}` for specific card grids

These are interpreted by the `anschmiegcv` theme templates for both HTML and PDF.

## Notes on alignment and consistency

- HTML and PDF are intended to stay in sync semantically.
- Timeline spacing and colors are derived from RenderCV-native values.
- HTML timeline-dot alignment uses exact CSS calculations rather than manual visual nudging.

## Fast start

1. Copy `example_data.yaml` and `example_design.yaml`
2. Edit your CV content in the data file
3. Adjust colors, spacing, and templates in the design file
4. Run `uv run cv render`
5. Check outputs in `rendercv_output/`
