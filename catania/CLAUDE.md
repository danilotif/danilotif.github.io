# Catania map

Static MapLibre GL map of Catania monuments and transit overlays.

## Files
- `index.html` — page shell, MapLibre setup, monument-marker rendering, generic overlay loader
- `monuments.json` — list of monuments (name, lat/lng, image, transparent flag)
- `map-layers.json` — declarative overlays (historic-centre polygon, axes, metro line, line-a). Each entry can specify `fill`, `outline`, `line`, and `markers`
- `images/` — monument PNGs (transparent cartoon-style, color-quantized)

## Adding a new overlay
Append an entry to `map-layers.json`. The generic `renderConfiguredLayer` in `index.html` handles `fill` / `outline` / `line` / `markers`. Marker `onFeatures` accepts `"all"` (default) or `"last"`. Optional `category` field (`"monuments"`, `"food"`, `"transportation"`) wires the overlay into the corresponding header toggle button.

## Header toggles
A burger button in the header opens a dropdown panel with toggles: monuments, food (placeholder), transportation, streets. State is tracked via `categoryRefs` (per-category map+HTML markers); `setCategoryVisible` flips MapLibre `visibility` and the marker element `display`. The panel closes on click-outside or Escape.

## Adding a new monument
Add an entry to `monuments.json` and drop its image into `images/`. Monuments whose image fails to load are silently skipped (no gray-circle placeholder).
