from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

_FONT_FACE_PATTERN = re.compile(
    r"@font-face\s*\{(?P<body>.*?)\}",
    re.DOTALL,
)
_CSS_VALUE_PATTERN = re.compile(r"(?P<key>font-family|font-style|font-weight|src):\s*(?P<value>[^;]+);")
_SRC_URL_PATTERN = re.compile(r"url\((?P<url>[^)]+)\)")
_REQUESTED_WEIGHTS = ("300", "400", "500", "600", "700")
_REQUESTED_ITAL_STYLES = ("0", "1")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _design_from_inputs(data_path: Path, design_path: Path | None) -> dict[str, Any]:
    data = _load_yaml(data_path)
    if design_path is None:
        return data.get("design", {}) if isinstance(data.get("design"), dict) else {}

    merged = _deep_merge(data, _load_yaml(design_path))
    design = merged.get("design", {})
    return design if isinstance(design, dict) else {}


def _font_families_from_design(design: dict[str, Any]) -> list[str]:
    typography = design.get("typography", {})
    if not isinstance(typography, dict):
        return []

    font_family = typography.get("font_family", {})
    if isinstance(font_family, str):
        candidates = [font_family]
    elif isinstance(font_family, dict):
        candidates = list(font_family.values())
    else:
        candidates = []

    families: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        family = candidate.strip()
        if family and family not in seen:
            seen.add(family)
            families.append(family)
    return families


def _family_request_spec(family: str) -> str:
    axis_values = ";".join(
        f"{italic},{weight}" for italic in _REQUESTED_ITAL_STYLES for weight in _REQUESTED_WEIGHTS
    )
    return f"{family}:ital,wght@{axis_values}"


def _download_css(family: str) -> str:
    url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote(
        _family_request_spec(family)
    ) + "&display=swap"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8")


def _parse_font_faces(css: str) -> list[dict[str, str]]:
    faces: list[dict[str, str]] = []
    for match in _FONT_FACE_PATTERN.finditer(css):
        body = match.group("body")
        data: dict[str, str] = {}
        for value_match in _CSS_VALUE_PATTERN.finditer(body):
            key = value_match.group("key")
            value = value_match.group("value").strip().strip('"').strip("'")
            data[key] = value

        src = data.get("src")
        if not src:
            continue
        src_match = _SRC_URL_PATTERN.search(src)
        if not src_match:
            continue
        data["url"] = src_match.group("url").strip().strip('"').strip("'")
        faces.append(data)
    return faces


def _family_cache_dir(fonts_root: Path, family: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", family.strip().lower()).strip("-")
    return fonts_root / "google" / slug


def _manifest_path(cache_dir: Path) -> Path:
    return cache_dir / "manifest.json"


def _save_manifest(cache_dir: Path, family: str, faces: list[dict[str, str]]) -> None:
    payload = {
        "family": family,
        "faces": [
            {
                "style": face.get("font-style", "normal"),
                "weight": face.get("font-weight", "400"),
                "url": face["url"],
                "file": Path(urllib.parse.urlparse(face["url"]).path).name,
            }
            for face in faces
        ],
    }
    _manifest_path(cache_dir).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _download_face(cache_dir: Path, face: dict[str, str]) -> None:
    font_url = face["url"]
    filename = Path(urllib.parse.urlparse(font_url).path).name
    destination = cache_dir / filename
    if destination.exists():
        return

    request = urllib.request.Request(font_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        destination.write_bytes(response.read())


def ensure_google_fonts_cached(data_path: Path, design_path: Path | None = None) -> None:
    fonts_root = data_path.resolve().parent / "fonts"
    fonts_root.mkdir(parents=True, exist_ok=True)

    design = _design_from_inputs(data_path.resolve(), design_path.resolve() if design_path else None)
    families = _font_families_from_design(design)

    for family in families:
        cache_dir = _family_cache_dir(fonts_root, family)

        try:
            css = _download_css(family)
            faces = _parse_font_faces(css)
            if not faces:
                continue

            cache_dir.mkdir(parents=True, exist_ok=True)
            for face in faces:
                _download_face(cache_dir, face)
            _save_manifest(cache_dir, family, faces)
        except Exception as exc:
            has_cached_fonts = cache_dir.exists() and any(cache_dir.glob("*.ttf"))
            if has_cached_fonts:
                print(
                    f"[cv] Warning: could not refresh Google font cache for '{family}': {exc}",
                    file=sys.stderr,
                )
                continue

            print(
                f"[cv] Warning: could not download Google font '{family}'; PDF will fall back to other available fonts. ({exc})",
                file=sys.stderr,
            )
