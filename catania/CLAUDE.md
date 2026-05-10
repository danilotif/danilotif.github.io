# Catania map

Static MapLibre GL map of Catania monuments and transit overlays.

## Files
- `index.html` — page shell, MapLibre setup, monument-marker rendering, generic overlay loader
- `map-data.json` — single source of truth for the map. Two top-level keys:
  - `monuments` — point markers (name, lat/lng, image, transparent flag, optional `category`)
  - `layers` — declarative overlays (historic-centre polygon, axes, metro line, line-a). Each entry can specify `fill`, `outline`, `line`, and `markers`
- `images/` — monument PNGs (transparent cartoon-style, color-quantized)

## Adding a new overlay
Append an entry to `layers` in `map-data.json`. The generic `renderConfiguredLayer` in `index.html` handles `fill` / `outline` / `line` / `markers`. Marker `onFeatures` accepts `"all"` (default) or `"last"`. Optional `category` field (`"monuments"`, `"food"`, `"transportation"`, `"streets"`) wires the overlay into the corresponding header toggle button.

## Header toggles
A burger button in the header opens a dropdown panel with toggles: monuments, food, transportation, streets. State is tracked via `categoryRefs` (per-category map+HTML markers); `setCategoryVisible` flips MapLibre `visibility` and the marker element `display`. Initial visibility derives from each button's `active` class — Transportation starts hidden by default. The panel closes on click-outside or Escape.

## Adding a new monument or food item
Add an entry to `monuments` in `map-data.json` (fields: `name`, `description`, `lat`, `lng`, `image`, `transparent`, `size`, optional `category`) and drop its image into `images/`. Items without `category` go under `monuments`; set `category: "food"` to put it under the Food toggle. Monuments whose image fails to load are silently skipped. Hovering shows the name; clicking opens a richer popup with name + description + a link to Google Maps.

## Rendering details
Monument features are grouped by category into one MapLibre source+layer per category (`monuments-<category>-layer`). All monument layer ids live in `monumentLayerIds` and are queried by a single map-level click/mousemove handler for popups and hover.
