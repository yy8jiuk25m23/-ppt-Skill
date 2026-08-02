#!/usr/bin/env python3
"""Inspect a PPTX for editable objects and suspicious full-slide images."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def natural_key(value: str) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)]


def integer_attr(node: ET.Element | None, name: str) -> int:
    if node is None:
        return 0
    try:
        return int(node.attrib.get(name, "0"))
    except ValueError:
        return 0


def slide_size(archive: zipfile.ZipFile) -> tuple[int, int]:
    root = ET.fromstring(archive.read("ppt/presentation.xml"))
    size = root.find("p:sldSz", NS)
    if size is None:
        return 0, 0
    return integer_attr(size, "cx"), integer_attr(size, "cy")


def image_bounds(pic: ET.Element) -> tuple[int, int, int, int]:
    xfrm = pic.find("p:spPr/a:xfrm", NS)
    if xfrm is None:
        return 0, 0, 0, 0
    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    return (
        integer_attr(off, "x"),
        integer_attr(off, "y"),
        integer_attr(ext, "cx"),
        integer_attr(ext, "cy"),
    )


def is_full_slide(bounds: tuple[int, int, int, int], width: int, height: int) -> bool:
    if width <= 0 or height <= 0:
        return False
    x, y, w, h = bounds
    tolerance_x = width * 0.025
    tolerance_y = height * 0.025
    return (
        abs(x) <= tolerance_x
        and abs(y) <= tolerance_y
        and w >= width * 0.95
        and h >= height * 0.95
    )


def inspect_slide(xml_bytes: bytes, width: int, height: int, name: str) -> dict[str, object]:
    root = ET.fromstring(xml_bytes)
    texts = [node.text or "" for node in root.findall(".//a:t", NS)]
    nonempty_texts = [text for text in texts if text.strip()]
    pictures = root.findall(".//p:pic", NS)
    full_slide_pictures = [pic for pic in pictures if is_full_slide(image_bounds(pic), width, height)]
    shapes = root.findall(".//p:sp", NS)
    connectors = root.findall(".//p:cxnSp", NS)
    graphic_frames = root.findall(".//p:graphicFrame", NS)
    groups = root.findall(".//p:grpSp", NS)

    editable_objects = len(shapes) + len(connectors) + len(graphic_frames) + len(groups)
    raster_only = bool(pictures) and editable_objects == 0 and not nonempty_texts
    warnings: list[str] = []
    if raster_only:
        warnings.append("slide appears raster-only")
    if full_slide_pictures:
        warnings.append("contains a near-full-slide picture; inspect for screenshot underlay")
    if pictures and not nonempty_texts:
        warnings.append("contains pictures but no editable text")

    return {
        "slide": name,
        "text_runs": len(nonempty_texts),
        "text_characters": sum(len(text) for text in nonempty_texts),
        "shapes": len(shapes),
        "connectors": len(connectors),
        "graphic_frames": len(graphic_frames),
        "groups": len(groups),
        "pictures": len(pictures),
        "full_slide_pictures": len(full_slide_pictures),
        "raster_only": raster_only,
        "warnings": warnings,
    }


def inspect_pptx(path: Path) -> dict[str, object]:
    with zipfile.ZipFile(path) as archive:
        width, height = slide_size(archive)
        slide_names = sorted(
            [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)],
            key=natural_key,
        )
        slides = [inspect_slide(archive.read(name), width, height, posixpath.basename(name)) for name in slide_names]

    return {
        "file": str(path.resolve()),
        "slide_size_emu": {"width": width, "height": height},
        "aspect_ratio": round(width / height, 6) if height else None,
        "is_16_9": bool(height and abs(width / height - 16 / 9) < 0.01),
        "slide_count": len(slides),
        "slides": slides,
    }


def print_human(report: dict[str, object]) -> None:
    print(f"File: {report['file']}")
    print(f"Slides: {report['slide_count']} | 16:9: {report['is_16_9']} | ratio: {report['aspect_ratio']}")
    for slide in report["slides"]:
        print(
            f"{slide['slide']}: text={slide['text_runs']} runs/{slide['text_characters']} chars, "
            f"shapes={slide['shapes']}, connectors={slide['connectors']}, "
            f"graphics={slide['graphic_frames']}, groups={slide['groups']}, pictures={slide['pictures']}"
        )
        for warning in slide["warnings"]:
            print(f"  WARNING: {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path, help="PowerPoint file to inspect")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a human-readable report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on non-16:9 files or raster-only slides",
    )
    parser.add_argument(
        "--allow-raster-only",
        action="store_true",
        help="Allow raster-only slides in strict mode when the reference is intentionally photographic",
    )
    args = parser.parse_args()

    if not args.pptx.is_file():
        parser.error(f"file not found: {args.pptx}")

    try:
        report = inspect_pptx(args.pptx)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        print(f"ERROR: invalid or unsupported PPTX: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    if not args.strict:
        return 0

    strict_failure = not report["is_16_9"]
    for slide in report["slides"]:
        strict_failure = strict_failure or (bool(slide["raster_only"]) and not args.allow_raster_only)
    return 1 if strict_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
