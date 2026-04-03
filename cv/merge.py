from __future__ import annotations

import copy
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DATA_SUFFIXES = ("_data.yaml", "_data.yml")
DESIGN_SUFFIXES = ("_design.yaml", "_design.yml")
DEFAULT_OUTPUT_SUFFIX = ".rendercv.yaml"


@dataclass
class ResolvedInputs:
    data_path: Path
    design_path: Path | None = None


def discover_default_input(cwd: Path) -> Path:
    candidates = sorted(path for suffix in DATA_SUFFIXES for path in cwd.glob(f"*{suffix}"))

    unique_candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_candidates.append(candidate)

    if not unique_candidates:
        raise ValueError(
            f"No '*_data.yaml' or '*_data.yml' file found in {cwd}. Pass a file path explicitly."
        )

    if len(unique_candidates) > 1:
        formatted = ", ".join(path.name for path in unique_candidates)
        raise ValueError(
            f"Multiple data files found in {cwd}: {formatted}. Pass a file path explicitly."
        )

    return unique_candidates[0]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")

    return data


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def _replace_suffix(name: str, suffixes: tuple[str, ...], replacement: str) -> str | None:
    for suffix in suffixes:
        if name.endswith(suffix):
            return f"{name[:-len(suffix)]}{replacement}"
    return None


def _find_existing(path_candidates: list[Path]) -> Path | None:
    existing = [candidate for candidate in path_candidates if candidate.exists()]

    if len(existing) > 1:
        formatted = ", ".join(str(path) for path in existing)
        raise ValueError(f"Multiple companion files found: {formatted}")

    return existing[0] if existing else None


def _data_companions(path: Path) -> Path | None:
    design_name = _replace_suffix(path.name, DATA_SUFFIXES, "_design.yaml")
    if design_name is None:
        return None

    return _find_existing(
        [
            path.with_name(design_name),
            path.with_name(design_name[:-5] + ".yml"),
        ]
    )


def _resolve_data_path(path: Path) -> tuple[Path, Path | None]:
    if any(path.name.endswith(suffix) for suffix in DATA_SUFFIXES):
        return path, _data_companions(path)

    data_name = _replace_suffix(path.name, DESIGN_SUFFIXES, "_data.yaml")
    if data_name is not None:
        data_path = _find_existing(
            [
                path.with_name(data_name),
                path.with_name(data_name[:-5] + ".yml"),
            ]
        )
        if data_path is None:
            raise ValueError(f"Expected companion data file next to {path.name}")

        return data_path, path

    return path, None


def _default_output_path(input_path: Path) -> Path:
    base = input_path
    for suffixes in (DATA_SUFFIXES, DESIGN_SUFFIXES):
        replacement = _replace_suffix(input_path.name, suffixes, "")
        if replacement is not None:
            base = input_path.with_name(replacement)
            break

    stem = base.stem if base.suffix else base.name
    return base.with_name(f"{stem}{DEFAULT_OUTPUT_SUFFIX}")


def resolve_inputs(input_path: Path) -> ResolvedInputs:
    resolved = input_path.resolve()
    data_path, design_path = _resolve_data_path(resolved)
    return ResolvedInputs(data_path=data_path, design_path=design_path)


def _merged_yaml_from_resolved_inputs(resolved: ResolvedInputs) -> dict[str, Any]:
    merged = _load_yaml(resolved.data_path)

    if resolved.design_path is not None:
        merged = _deep_merge(merged, _load_yaml(resolved.design_path))

    return merged


def merge_to_file(input_path: Path, *, output_path: Path | None = None) -> Path:
    resolved = resolve_inputs(input_path)
    merged_data = _merged_yaml_from_resolved_inputs(resolved)
    destination = (output_path or _default_output_path(input_path.resolve())).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(merged_data, handle, sort_keys=False, allow_unicode=True)

    return destination


def render_cv(input_path: Path, *, extra_rendercv_args: list[str] | None = None) -> None:
    resolved = resolve_inputs(input_path)
    extras = extra_rendercv_args or []
    command = [sys.executable, "-m", "cv.rendercv_wrapper", "render", str(resolved.data_path)]

    if resolved.design_path is not None:
        command.extend(["--design", str(resolved.design_path)])

    command.extend(extras)
    subprocess.run(command, check=True)
