# AGENTS.md

This repository must remain a thin extension of RenderCV.

## Architectural Intent

- Treat this repo as two things only:
  - a custom RenderCV theme named `anschmiegcv`
  - a very thin helper layer in `cv` / `cv_tools`
- The RenderCV theme must follow the RenderCV theme specification and conventions as closely as possible.
- The helper layer must stay intentionally small and must not evolve into a second rendering system.

## Source of Truth

- RenderCV’s native schema, theme model, template structure, spacing settings, color settings, and typography settings are the canonical source of truth.
- Prefer using existing RenderCV fields and template behavior over introducing repo-specific configuration.
- If HTML and PDF need the same behavior, derive both from the same RenderCV-native design values.
- Avoid hardcoded visual values when an equivalent RenderCV design token already exists.
- For CSS and HTML layout math, prefer exact formulas derived from RenderCV tokens over manual visual nudging.

## Theme Rules

- The RenderCV theme name is `anschmiegcv`.
- The Python package name may be `cv`; do not rename the RenderCV theme away from `anschmiegcv`.
- Theme templates should remain compatible with RenderCV’s expected theme folder layout and naming.
- Any custom theme behavior should feel like a thin overlay on top of RenderCV, not a fork of RenderCV.

## Helper Rules

- The CLI/helper should only do non-conflicting orchestration tasks.
- Good helper responsibilities:
  - discovering the default `*_data.yaml`
  - pairing `*_data.yaml` with `*_design.yaml`
  - forwarding arguments to native RenderCV commands
  - small compatibility aliases
- Avoid helper responsibilities that duplicate or override RenderCV-native behavior.
- Do not add helper-owned configuration formats unless absolutely necessary.
- Do not reimplement RenderCV rendering, layout, schema, or document generation logic in the helper.

## Styling and Layout

- Keep defaults and fallbacks subtle and sane.
- Custom styling should only override behavior when the template explicitly asks for it.
- Default/fallback formatting should resolve to RenderCV-native colors, spacing, typography, and layout settings.
- Do not introduce conflicting style definitions across Typst and HTML.
- HTML and PDF should follow the same semantic rules whenever possible.
- When alignment depends on font size, line height, border width, or spacing tokens, compute it directly from those values.

## Template Formatting Extensions

- Template-string enhancements must remain lightweight and compatible with RenderCV’s design system.
- Prefer existing or broadly recognizable syntax over inventing large custom mini-languages.
- Any inline styling syntax must resolve through RenderCV-native design values where possible.
- Extensions should degrade gracefully when not used.

## Change Discipline

- Favor minimal, surgical changes.
- Do not add new abstraction layers unless they clearly reduce conflict with RenderCV.
- Before adding custom behavior, ask: “Can RenderCV already do this natively?”
- If the answer is yes, use the native RenderCV path.
- If the answer is no, implement the smallest possible overlay.

## Validation

- Validate both PDF/Typst and HTML output after changing theme templates, helper behavior, spacing, or styling logic.
- Watch specifically for drift between HTML and PDF in:
  - colors
  - spacing
  - typography
  - template ordering
  - inline emphasis / markdown rendering
