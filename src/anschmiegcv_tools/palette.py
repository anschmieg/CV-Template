from __future__ import annotations

import colorsys
import re
from dataclasses import dataclass
from typing import Iterable

RGB = tuple[int, int, int]

_HEX_PATTERN = re.compile(r"^#?(?P<value>[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_PATTERN = re.compile(
    r"^rgb\(\s*(?P<r>\d{1,3})\s*,\s*(?P<g>\d{1,3})\s*,\s*(?P<b>\d{1,3})\s*\)$",
    re.IGNORECASE,
)
_HSL_PATTERN = re.compile(
    r"^hsl\(\s*(?P<h>-?\d+(?:\.\d+)?)\s*,\s*(?P<s>\d+(?:\.\d+)?)%\s*,\s*(?P<l>\d+(?:\.\d+)?)%\s*\)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class PaletteOptions:
    """Palette generation options."""

    min_body_contrast: float = 7.0
    min_secondary_contrast: float = 4.5
    min_accent_contrast: float = 3.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _to_rgb_tuple(color: str) -> RGB:
    text = color.strip()

    hex_match = _HEX_PATTERN.match(text)
    if hex_match:
        value = hex_match.group("value")
        if len(value) == 3:
            value = "".join(ch * 2 for ch in value)
        return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))

    rgb_match = _RGB_PATTERN.match(text)
    if rgb_match:
        r = int(rgb_match.group("r"))
        g = int(rgb_match.group("g"))
        b = int(rgb_match.group("b"))
        if any(channel > 255 for channel in (r, g, b)):
            raise ValueError(f"Invalid rgb color '{color}': channels must be <= 255")
        return (r, g, b)

    hsl_match = _HSL_PATTERN.match(text)
    if hsl_match:
        h = float(hsl_match.group("h")) % 360.0
        s = _clamp(float(hsl_match.group("s")) / 100.0, 0.0, 1.0)
        l = _clamp(float(hsl_match.group("l")) / 100.0, 0.0, 1.0)
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
        return (round(r * 255), round(g * 255), round(b * 255))

    raise ValueError(
        f"Unsupported color format '{color}'. Use #RRGGBB/#RGB, rgb(...), or hsl(...)."
    )


def _rgb_to_hls(rgb: RGB) -> tuple[float, float, float]:
    r, g, b = rgb
    return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)


def _hls_to_rgb(h: float, l: float, s: float) -> RGB:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, _clamp(l, 0.0, 1.0), _clamp(s, 0.0, 1.0))
    return (round(r * 255), round(g * 255), round(b * 255))


def _shift_hls(
    rgb: RGB,
    *,
    hue_shift: float = 0.0,
    sat_mult: float = 1.0,
    sat_add: float = 0.0,
    light_mult: float = 1.0,
    light_add: float = 0.0,
) -> RGB:
    h, l, s = _rgb_to_hls(rgb)
    new_h = (h + hue_shift) % 1.0
    new_s = _clamp(s * sat_mult + sat_add, 0.0, 1.0)
    new_l = _clamp(l * light_mult + light_add, 0.0, 1.0)
    return _hls_to_rgb(new_h, new_l, new_s)


def _relative_luminance(rgb: RGB) -> float:
    def transform(channel: int) -> float:
        value = channel / 255.0
        if value <= 0.03928:
            return value / 12.92
        return ((value + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * transform(r) + 0.7152 * transform(g) + 0.0722 * transform(b)


def _contrast_ratio(fg: RGB, bg: RGB = (255, 255, 255)) -> float:
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _ensure_min_contrast(
    rgb: RGB,
    min_ratio: float,
    *,
    against: RGB = (255, 255, 255),
) -> RGB:
    if _contrast_ratio(rgb, against) >= min_ratio:
        return rgb

    h, l, s = _rgb_to_hls(rgb)
    adjusted = rgb
    for step in range(1, 40):
        candidate = _hls_to_rgb(h, _clamp(l - step * 0.02, 0.0, 1.0), s)
        if _contrast_ratio(candidate, against) >= min_ratio:
            adjusted = candidate
            break
    return adjusted


def _as_rgb_string(rgb: RGB) -> str:
    return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"


def build_semantic_palette(
    seed: str,
    accent_seed: str | None = None,
    *,
    options: PaletteOptions | None = None,
) -> dict[str, str]:
    """Build deterministic semantic RenderCV palette from one or two seed colors."""
    opts = options or PaletteOptions()
    primary = _to_rgb_tuple(seed)
    accent = _to_rgb_tuple(accent_seed) if accent_seed else _shift_hls(primary, hue_shift=0.07)

    body = _shift_hls(primary, sat_mult=0.35, light_mult=0.45, light_add=0.03)
    body = _ensure_min_contrast(body, opts.min_body_contrast)

    name = _ensure_min_contrast(primary, opts.min_accent_contrast)
    headline = _shift_hls(primary, sat_mult=0.95, light_mult=0.88)
    headline = _ensure_min_contrast(headline, opts.min_accent_contrast)

    section_titles = _shift_hls(accent, sat_mult=1.05, light_mult=0.8)
    section_titles = _ensure_min_contrast(section_titles, opts.min_accent_contrast)

    links = _shift_hls(primary, sat_mult=1.1, light_mult=0.82)
    links = _ensure_min_contrast(links, opts.min_accent_contrast)

    connections = _shift_hls(primary, sat_mult=0.45, light_mult=0.58, light_add=0.03)
    connections = _ensure_min_contrast(connections, opts.min_secondary_contrast)

    footer = _shift_hls(primary, sat_mult=0.20, light_mult=0.73)
    footer = _ensure_min_contrast(footer, opts.min_secondary_contrast)

    top_note = _shift_hls(primary, sat_mult=0.17, light_mult=0.76)
    top_note = _ensure_min_contrast(top_note, opts.min_secondary_contrast)

    timeline_dot = _shift_hls(accent, sat_mult=1.1, light_mult=0.85)
    timeline_dot = _ensure_min_contrast(timeline_dot, opts.min_accent_contrast)

    timeline_line = _shift_hls(accent, sat_mult=0.92, light_mult=1.0, light_add=0.06)
    timeline_line = _ensure_min_contrast(timeline_line, opts.min_accent_contrast)

    return {
        "body": _as_rgb_string(body),
        "name": _as_rgb_string(name),
        "headline": _as_rgb_string(headline),
        "connections": _as_rgb_string(connections),
        "section_titles": _as_rgb_string(section_titles),
        "links": _as_rgb_string(links),
        "footer": _as_rgb_string(footer),
        "top_note": _as_rgb_string(top_note),
        "timeline_dot": _as_rgb_string(timeline_dot),
        "timeline_line": _as_rgb_string(timeline_line),
    }


def list_supported_formats() -> Iterable[str]:
    return ("#RRGGBB", "#RGB", "rgb(r,g,b)", "hsl(h,s%,l%)")
