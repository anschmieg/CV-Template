# CV-Template

This repo now centers on two things:

- the local `cv` RenderCV theme
- a very small `cv` CLI wrapper that detects split YAML inputs and forwards them to RenderCV

## Layout

- `cv/`: the RenderCV theme
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

- The theme name is `cv`.
- Section title directives like `{.cards}` and `{.timeline}` are handled by the theme templates.
- Theme-specific colors `timeline_dot` and `timeline_line` are supported through `cv/__init__.py`.

## Screenshots

![Screenshot - Desktop 1](pics/screenshots/desktop-1.png)
![Screenshot - Desktop 2](pics/screenshots/desktop-2.png)
