"""Backward-compatibility shim for the renamed cv helper package."""

from cv.merge import discover_default_input, merge_to_file, render_cv, resolve_inputs

__all__ = ["discover_default_input", "merge_to_file", "render_cv", "resolve_inputs"]
