---
name: image-to-editable-pptx
description: Reconstruct reference images or screenshots as high-fidelity, fully editable 16:9 PowerPoint files. Use when a user asks to convert an image, screenshot, poster, infographic, dashboard, diagram, chart, or slide preview into a .pptx while preserving layout, colors, typography, text, arrows, cards, and visual style; requires OCR text to become editable text boxes, simple visuals to become native PowerPoint objects, and forbids using the source image as a full-slide background.
---

# Image to Editable PowerPoint

Rebuild each reference image as a semantic PowerPoint slide whose elements can be selected, moved, and edited independently. Treat the reference as a visual contract, not as a background asset.

## Apply the presentation engine

Read and follow the installed `Presentations` skill before implementation. Use its current JavaScript presentation engine, rendering helpers, output conventions, and overlap checks. Do not use `python-pptx`.

Use this skill to specialize the reconstruction workflow. If a generic presentation rule conflicts with explicit reconstruction requirements, preserve the user's reference fidelity and editability while still satisfying safety and output-format constraints.

## Prepare the job

1. Map one reference image to one slide unless the user specifies another mapping.
2. Create a 16:9 deck at 13.333 × 7.5 inches.
3. Put intermediate files in the task work directory and only the final `.pptx` in the requested output directory.
4. Inspect every reference at original resolution. Rasterize unsupported inputs without changing aspect ratio.
5. Read [references/reconstruction-playbook.md](references/reconstruction-playbook.md) before building slides.

For a non-16:9 reference, preserve all content and reconstruct it within 16:9. Do not stretch the source or silently crop meaningful content. Use proportionate margins or visually plausible extension; state any material adaptation in the handoff.

## Build a reconstruction ledger

Before coding, record for each slide:

- canvas and major region bounds;
- exact visible text, language, line breaks, alignment, hierarchy, and likely font;
- background, fills, borders, gradients, shadows, transparency, and corner radii;
- photos or complex raster art that may remain images;
- charts, arrows, connectors, icons, cards, tables, and decorative geometry to rebuild natively;
- front-to-back layer order and intentional overlaps.

Measure positions in normalized reference coordinates, then map them to the PowerPoint canvas. Do not place by intuition alone.

## Reconstruct semantically

Build in this order:

1. base background shapes and large color fields;
2. cropped photographic or highly complex raster regions;
3. connectors and arrows that must sit behind nodes;
4. charts, tables, cards, blocks, icons, and other native geometry;
5. editable text boxes;
6. foreground accents, masks, and small finishing details.

Follow these hard rules:

- Never paste the whole reference image as a slide background or full-slide picture.
- Convert every visible word outside an allowed complex raster region into editable text.
- Keep logical text units in separate text boxes; do not flatten a paragraph, label, and number into one bitmap.
- Rebuild simple charts, arrows, connectors, cards, tables, badges, dividers, and color blocks with native PowerPoint objects.
- Use a native chart when its data can be recovered reliably. Otherwise use editable shapes while preserving the visible values and labels.
- Crop only the photographic or genuinely complex illustration region from the source. Do not include adjacent captions or annotations in the crop.
- Match font family when identifiable. Otherwise choose the closest installed font, then tune size, weight, tracking, line spacing, and box geometry to match the render.
- Preserve intentional overlaps but fix accidental ones. Keep connectors behind nodes and labels.
- Group related multi-part objects when this improves manipulation without making their text uneditable.

## Verify and iterate

Read [references/qa-checklist.md](references/qa-checklist.md) and complete every applicable check.

For each iteration:

1. Export the `.pptx`.
2. Render every slide to PNG with the presentation skill's render helper.
3. Inspect every rendered slide individually at full size.
4. Compare each render with its reference using `scripts/compare_reference.py` when Pillow is available.
5. Fix geometry, typography, color, crop, wrapping, clipping, layering, and connector issues.
6. Run the presentation skill's overflow test.
7. Run `scripts/verify_editability.py <deck.pptx> --strict` and investigate every warning.
8. Repeat until both fidelity and editability pass.

Numerical similarity scores are diagnostic, not acceptance by themselves. Font rasterization and antialiasing can lower a score even when the slide is correct; full-size visual inspection remains mandatory.

## Deliver

Deliver only the final 16:9 `.pptx` unless the user asks for previews or source code. Briefly state:

- that text and native objects are independently editable;
- which complex regions remain raster images, if any;
- any font substitution or non-16:9 adaptation that materially affects fidelity.

Do not claim full editability if text remains embedded in a raster crop or if any slide is only a screenshot.
