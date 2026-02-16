
from typing import Literal

import pydantic
from rendercv.schema.models.base import BaseModelWithoutExtraKeys
from rendercv.schema.models.design.classic_theme import (
    ClassicTheme,
    Colors as ClassicColors,
)
from rendercv.schema.models.design.color import Color


class Colors(ClassicColors):
    """Color extensions unique to anschmiegcv theme."""

    timeline_dot: Color | None = pydantic.Field(
        default=None,
        description="Optional timeline dot color; falls back to connections color.",
    )
    timeline_line: Color | None = pydantic.Field(
        default=None,
        description="Optional timeline line color; falls back to connections color.",
    )


class AnschmiegcvTheme(ClassicTheme, BaseModelWithoutExtraKeys):
    """Custom theme model used by RenderCV for anschmiegcv templates."""

    theme: Literal["anschmiegcv"] = "anschmiegcv"
    colors: Colors = pydantic.Field(default_factory=Colors)
