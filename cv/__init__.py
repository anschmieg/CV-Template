from __future__ import annotations

from typing import Literal

import pydantic
from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.classic_theme import (
    ClassicTheme,
    Colors as ClassicColors,
)
from rendercv.schema.models.design.color import Color


def _clamp_channel(value: float) -> int:
    return max(0, min(255, round(value)))


def _rgb_tuple(color: Color) -> tuple[int, int, int]:
    return color.as_rgb_tuple()


def _from_rgb(rgb: tuple[float, float, float]) -> Color:
    red, green, blue = (_clamp_channel(channel) for channel in rgb)
    return Color(f"rgb({red}, {green}, {blue})")


def _mix(left: Color, right: Color, ratio: float) -> Color:
    left_rgb = _rgb_tuple(left)
    right_rgb = _rgb_tuple(right)
    return _from_rgb(
        tuple(
            left_channel * (1 - ratio) + right_channel * ratio
            for left_channel, right_channel in zip(left_rgb, right_rgb, strict=True)
        )
    )


class Colors(ClassicColors):
    """Color extensions unique to the cv theme."""

    accent: Color | None = pydantic.Field(
        default=None,
        description="Optional accent color used to derive the theme palette.",
    )
    base: Color | None = pydantic.Field(
        default=None,
        description="Optional base body color used to derive the theme palette.",
    )
    timeline_dot: Color | None = pydantic.Field(
        default=None,
        description="Optional timeline dot color; falls back to section title color.",
    )
    timeline_line: Color | None = pydantic.Field(
        default=None,
        description="Optional timeline line color; falls back to section title color.",
    )


def _generated_palette(colors: Colors) -> dict[str, Color]:
    accent = colors.accent
    if accent is None:
        return {}

    base = colors.base or colors.body
    white = Color("rgb(255, 255, 255)")

    name = accent
    headline = accent
    section_titles = accent
    connections = accent
    links = accent
    footer = _mix(base, white, 0.18)
    top_note = _mix(base, white, 0.12)

    return {
        "body": base,
        "name": name,
        "headline": headline,
        "section_titles": section_titles,
        "links": links,
        "connections": connections,
        "footer": footer,
        "top_note": top_note,
        "timeline_dot": section_titles,
        "timeline_line": section_titles,
    }


class CvTheme(ClassicTheme, BaseModelWithoutExtraKeys):
    """Custom theme model used by RenderCV for cv templates."""

    theme: Literal["anschmiegcv"] = "anschmiegcv"
    colors: Colors = pydantic.Field(default_factory=Colors)

    @pydantic.model_validator(mode="after")
    def apply_generated_palette(self) -> "CvTheme":
        generated = _generated_palette(self.colors)
        if not generated:
            return self

        explicit_fields = set(self.colors.model_fields_set)
        for field_name, value in generated.items():
            if field_name not in explicit_fields:
                setattr(self.colors, field_name, value)

        return self
