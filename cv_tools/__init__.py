"""Backward-compatibility shim for helper utilities that now live under cv."""

from cv.merge import discover_default_input, merge_to_file, render_cv, resolve_inputs

__all__ = ["discover_default_input", "merge_to_file", "render_cv", "resolve_inputs"]
