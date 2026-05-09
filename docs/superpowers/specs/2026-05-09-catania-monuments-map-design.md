# Catania Monuments Map — Design

Date: 2026-05-09
Status: Draft (awaiting user review)

## Goal

Add a new sub-page to the static site showing a zoomable real-world map of Catania with 5 monument thumbnails placed at their real geographic locations. Clicking a thumbnail opens that location on Google Maps.

## Non-goals

- Clustering, search, filters, list view, detail pages, sharing, multi-city support.
- Any build step or framework. The repo is a plain GitHub Pages static site.

## File structure

```
catania/
  index.html
  monuments.json
  images/
    <one image file per monument, paths referenced from monuments.json>
```

This mirrors the existing pattern of `food/`, `games/`, `i-hate-ads/` sub-pages.

## Tech stack

- **Renderer:** MapLibre GL JS (open source, no API key) loaded from a CDN (unpkg or jsdelivr), pinned to a specific minor version at implementation time.
- **Tile style:** OpenFreeMap "liberty" style: `https://tiles.openfreemap.org/styles/liberty`. Free, no API key, no rate limits, OSM-based.
- **Language:** Vanilla HTML/CSS/JS. No build step. Consistent with the rest of the repo.

## Map configuration

- **Center:** Catania (~`[15.0830, 37.5079]` in `[lng, lat]` order as MapLibre expects).
- **Zoom limits:** `minZoom: 12` (whole city visible), `maxZoom: 17` (street level).
- **Initial zoom:** 13.
- **Pan limits:** `maxBounds` set to a bounding box around Catania so the user cannot pan to unrelated regions. Approximate bounds: SW `[14.97, 37.44]`, NE `[15.18, 37.56]` (will be tuned during implementation).
- **Controls:** Default `NavigationControl` (zoom in/out + compass) in the top-right.
- **Attribution:** MapLibre's default `AttributionControl` is left enabled, which surfaces OpenStreetMap and OpenFreeMap credits in the corner — required by OSM's license.

## Monument markers

- Each marker is a custom HTML element: a circular `<div>` (~50px diameter) with the monument image as `background-image: cover`, a 2px white border, and a soft drop shadow for legibility on the map.
- Created via `new maplibregl.Marker({ element }).setLngLat([lng, lat]).addTo(map)`.
- HTML markers do not scale with zoom by default — this gives the requested constant-size thumbnail behavior at all zoom levels.
- **Hover:** browser-native `title` attribute on the element shows the monument name.
- **Click:** opens Google Maps in a new tab via:
  `window.open('https://www.google.com/maps/search/?api=1&query=' + lat + ',' + lng, '_blank', 'noopener')`.

## Data format

`catania/monuments.json`:

```json
[
  {
    "name": "Cattedrale di Sant'Agata",
    "lat": 37.5026,
    "lng": 15.0876,
    "image": "images/cattedrale.jpg"
  }
]
```

5 entries total. Coordinates use decimal degrees. Image paths are relative to `catania/index.html`. The user supplies the images and final coordinates; the page reads the JSON at startup via `fetch('monuments.json')`.

## Page chrome

- Header bar with the title "Catania" on the left and a "← Back to home" link on the right, matching the look of `food/index.html`.
- Map container fills the rest of the viewport (full height minus header).
- `<title>`, favicon (`../assets/img/favicon.png`), and `<meta viewport>` consistent with other pages.

## Error handling (boundaries only)

- If `fetch('monuments.json')` fails or returns malformed data, log to console and render the map without markers. No user-facing error UI — internal data file under our control.
- Missing image file: browser shows a broken-image background; acceptable for this scope.

## Out of scope (YAGNI)

- Marker clustering — only 5 points.
- Responsive marker sizing, custom popups, animation, fullscreen control.
- Localization, analytics, SEO metadata beyond `<title>`.
- Tests — static page with no logic beyond library wiring.

## Open inputs from user (needed at implementation time)

- 5 monument images (file names + actual files placed in `catania/images/`).
- Final monument names and lat/lng for each.
