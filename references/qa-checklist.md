# Fidelity and Editability QA

## Contents

1. Structural checks
2. Visual checks
3. Text checks
4. Native-object checks
5. Delivery gate

## 1. Structural checks

- Confirm the deck is 16:9 and every reference maps to the intended slide.
- Confirm the slide contains native shapes, text, charts, tables, connectors, or groups as appropriate.
- Confirm no complete or near-complete source screenshot is used as an underlay or full-slide picture.
- Confirm all elements stay inside the slide canvas unless the overflow is intentional and invisible.
- Confirm the file opens, renders, and can be edited without repair warnings.

Run:

```bash
python scripts/verify_editability.py final.pptx --strict
```

Treat a full-slide image warning as a manual-review blocker even when the script does not fail.
Use `--allow-raster-only` only when the source slide is intentionally a photograph or a genuinely inseparable complex illustration with no reconstructable text or native objects.

## 2. Visual checks

Inspect every rendered slide at full size beside the reference. Check:

- outer margins, major regions, repeated gaps, alignment, and symmetry;
- object bounds, rotations, corner radii, and layer order;
- fills, gradients, transparency, borders, shadows, and decorative accents;
- raster crops, masks, aspect ratios, and sharpness;
- chart scales, plot areas, markers, legends, and data-label positions;
- arrow endpoints and connectors passing behind, not through, nodes;
- accidental overlap, clipping, wrapping, or hidden elements.

Use the comparison script to produce a difference image:

```bash
python scripts/compare_reference.py reference.png rendered.png --diff diff.png
```

Use the score to locate regressions across iterations, not as a substitute for inspection.

## 3. Text checks

- Select representative title, body, label, metric, and footnote text in PowerPoint and confirm it is editable.
- Compare every line against the source for copy, punctuation, numbers, units, and language.
- Match font family or disclose the fallback.
- Match size, weight, color, line spacing, tracking, alignment, and text-box margins.
- Confirm intended single-line text does not wrap.
- Confirm no external label or annotation remains baked into a raster crop.

## 4. Native-object checks

- Select and move a card, arrow, connector, color block, chart, table, and icon where present.
- Confirm chart labels and visible values are editable and accurate.
- Confirm connectors stay attached or remain visually correct after small movements.
- Confirm grouped assemblies can be ungrouped and edited.
- Confirm complex raster regions are tightly cropped and contain no avoidable editable content.

## 5. Delivery gate

Do not deliver until all of the following are true:

- every slide has been rendered and inspected individually;
- all unintended overlap, clipping, overflow, and wrapping issues are fixed;
- the source image is not being used as a full-slide shortcut;
- all visible text that should be editable is editable;
- the reconstructed slide matches the reference's layout, palette, hierarchy, and style at normal viewing size;
- any unavoidable font substitution, uncertain copy, raster region, or aspect-ratio adaptation is disclosed.
