# Reconstruction Playbook

## Contents

1. Source inspection
2. Geometry mapping
3. Text and typography
4. Color and effects
5. Native object reconstruction
6. Raster-region policy
7. Layering and grouping
8. Special cases

## 1. Source inspection

Inspect the reference at original resolution. Record its pixel width and height and determine whether it is a direct slide export, a screen capture with browser or app chrome, or a photograph of a display.

Remove only unambiguous capture chrome from the measured slide region. If the slide boundary is uncertain, keep the visible composition intact.

Create a visual inventory from large regions to small details. Use the image itself as the authority for visible copy. OCR is a starting point; manually verify every line, number, unit, punctuation mark, and line break against the source.

## 2. Geometry mapping

Use normalized coordinates so the reconstruction is resolution-independent:

```text
x_slide = x_pixel / reference_width × slide_width
y_slide = y_pixel / reference_height × slide_height
w_slide = w_pixel / reference_width × slide_width
h_slide = h_pixel / reference_height × slide_height
```

Measure major edges first: outer margins, columns, bands, card grids, chart plot areas, and baselines. Then position inner details relative to their parent region. Preserve repeated gaps and alignments as a system instead of tuning every object independently.

Estimate rotation from reference edges and use the same angle for related objects. For photographed slides, correct obvious perspective distortion before measuring if a lossless or near-lossless correction is possible.

## 3. Text and typography

Create editable text boxes for all visible external text. Preserve:

- exact copy and language;
- capitalization and punctuation;
- line breaks and no-wrap behavior;
- font family, weight, size, color, and transparency;
- horizontal and vertical alignment;
- paragraph spacing, line spacing, indentation, and bullets;
- character spacing when needed for matching;
- text-box margins and rotation.

Use the smallest logical text unit that remains convenient to edit. A title, subtitle, body paragraph, metric, axis label, legend item, and footnote should normally be separate objects.

When the exact font is unavailable, choose the closest installed font by proportions and stroke character. Prefer stable CJK fallbacks such as PingFang SC on macOS or Microsoft YaHei where appropriate, but match the reference rather than applying a universal default. Record material substitutions.

Do not solve overflow by shrinking text indiscriminately. First correct box width, internal margins, line spacing, and font choice. Preserve single-line titles as single lines.

## 4. Color and effects

Sample colors from flat interior pixels, away from antialiased edges. Record colors as RGB or hex and preserve opacity separately. Rebuild gradients with matching direction and stop positions where supported.

Match border width, dash pattern, corner radius, blur-like softness, shadow direction, shadow opacity, and highlight accents. When an effect is unsupported, approximate it with the least complex editable construction and verify at normal viewing size.

## 5. Native object reconstruction

Prefer semantic native objects:

- rectangles, rounded rectangles, circles, polygons, lines, and freeform shapes for color fields and cards;
- connectors for relationships and callouts;
- native tables for real tabular data;
- native charts when values and series can be recovered;
- editable shape assemblies for simple icons and diagrams;
- separate editable labels for all external annotations.

For charts, recover visible labels, values, axes, scales, tick spacing, legend order, colors, and marker styles. If hidden data cannot be inferred, reproduce only what the image proves and do not invent values.

For icons, use simple PowerPoint geometry when the silhouette is practical. A small complex logo or intricate illustration may remain a tightly cropped transparent image, but its surrounding copy must remain editable.

## 6. Raster-region policy

Allow raster images only for photographs, textured artwork, detailed illustrations, complex logos, or other content whose semantic reconstruction would be disproportionate and visually worse.

Crop tightly to the allowed region. The crop must not include captions, legends, axis labels, arrows, callouts, badges, or other text that should be editable. Preserve the original crop, mask shape, transparency, and aspect ratio.

Never use the complete reference image, or a near-complete reference image, as an underlay to fake fidelity. Do not hide such an image behind editable objects.

## 7. Layering and grouping

Establish explicit layer order. Put backgrounds at the back, connectors before nodes, photo regions below their labels, and finishing accents last. Check every intentional overlap against the reference.

Group multi-part icons, chart legends, or card assemblies when useful. Avoid giant groups that make normal text editing cumbersome. Ensure each group can still be ungrouped without losing semantics.

## 8. Special cases

For multiple references, preserve their order and use one source-to-slide mapping unless instructed otherwise.

For a reference with animation states, reconstruct the shown state only unless the user asks for animation.

For inaccessible or illegible copy, do not hallucinate. Use the clearest recoverable reading and disclose uncertainty, or ask for a higher-resolution source when the missing text is material.

For non-16:9 references, preserve content and composition within a 16:9 canvas. Prefer proportional margins or a deliberate background extension over stretching. Do not invent or crop important content silently.
