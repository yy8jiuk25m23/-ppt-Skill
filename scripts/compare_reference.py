#!/usr/bin/env python3
"""Compare a reference image with a rendered slide and optionally save a diff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat
except ImportError as exc:  # pragma: no cover - environment-dependent message
    raise SystemExit("Pillow is required: install the 'Pillow' Python package") from exc


def similarity(diff: Image.Image) -> float:
    means = ImageStat.Stat(diff).mean
    mean_error = sum(means) / len(means)
    return max(0.0, 100.0 * (1.0 - mean_error / 255.0))


def compare(reference_path: Path, render_path: Path, diff_path: Path | None) -> dict[str, object]:
    with Image.open(reference_path) as reference_source, Image.open(render_path) as render_source:
        reference = reference_source.convert("RGB")
        render = render_source.convert("RGB")
        original_reference_size = reference.size
        if reference.size != render.size:
            reference = reference.resize(render.size, Image.Resampling.LANCZOS)

        pixel_diff = ImageChops.difference(reference, render)
        reference_edges = reference.convert("L").filter(ImageFilter.FIND_EDGES)
        render_edges = render.convert("L").filter(ImageFilter.FIND_EDGES)
        edge_diff = ImageChops.difference(reference_edges, render_edges)

        if diff_path is not None:
            diff_path.parent.mkdir(parents=True, exist_ok=True)
            emphasized = ImageEnhance.Contrast(pixel_diff).enhance(3.0)
            emphasized.save(diff_path)

        return {
            "reference": str(reference_path.resolve()),
            "render": str(render_path.resolve()),
            "reference_size": list(original_reference_size),
            "render_size": list(render.size),
            "reference_resized_for_comparison": original_reference_size != render.size,
            "pixel_similarity_percent": round(similarity(pixel_diff), 3),
            "edge_similarity_percent": round(similarity(edge_diff.convert("RGB")), 3),
            "diff": str(diff_path.resolve()) if diff_path is not None else None,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, help="Reference image")
    parser.add_argument("render", type=Path, help="Rendered slide image")
    parser.add_argument("--diff", type=Path, help="Optional output path for an emphasized difference image")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    for path in (args.reference, args.render):
        if not path.is_file():
            parser.error(f"file not found: {path}")

    try:
        report = compare(args.reference, args.render, args.diff)
    except OSError as exc:
        print(f"ERROR: unable to read or write image: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Pixel similarity: {report['pixel_similarity_percent']}%")
        print(f"Edge similarity: {report['edge_similarity_percent']}%")
        if report["reference_resized_for_comparison"]:
            print(f"Reference resized from {tuple(report['reference_size'])} to {tuple(report['render_size'])}")
        if report["diff"]:
            print(f"Diff: {report['diff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
