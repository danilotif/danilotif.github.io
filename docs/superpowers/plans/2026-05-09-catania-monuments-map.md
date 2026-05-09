# Catania Monuments Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/catania/` static sub-page showing a zoomable real-world map with 5 monument thumbnails that open Google Maps on click.

**Architecture:** Single HTML page in `catania/index.html`. MapLibre GL JS renders a real map using OpenFreeMap vector tiles (no API key). Monument data lives in `catania/monuments.json` and is fetched at startup. Each monument is a constant-size custom HTML marker; clicking opens `https://www.google.com/maps/search/?api=1&query=lat,lng` in a new tab.

**Tech Stack:** Vanilla HTML/CSS/JS (no build step), MapLibre GL JS (CDN), OpenFreeMap "liberty" style.

**Spec:** `docs/superpowers/specs/2026-05-09-catania-monuments-map-design.md`

**Project conventions you must follow:**
- This is a static GitHub Pages site. Sub-pages live in top-level directories (`food/`, `games/`, `i-hate-ads/`). No build tools, no package.json.
- Libraries are loaded from CDN inside `<head>`.
- Favicon path used by other pages: `../assets/img/favicon.png`.
- "Back to home" link points to `../index.html`.
- The user prefers **no auto-commits**. Every commit step in this plan is a *manual checkpoint*: the engineer should pause, show the diff, and only run the `git commit` after explicit user approval.

**Local preview command:** From the repo root, run `python3 -m http.server 8000` and open `http://localhost:8000/catania/`. (MapLibre's `fetch` for `monuments.json` will not work via `file://` due to CORS; you must use a local server.)

---

## File Structure

Files this plan creates:

- `catania/index.html` — page chrome, MapLibre init, marker rendering, click handler. Single file, ~100 lines.
- `catania/monuments.json` — array of 5 monument records.
- `catania/images/` — directory for monument images. The user supplies the actual image files; the plan creates the directory and references the expected file names in `monuments.json`.

No shared CSS / JS module is introduced. Keeping everything in one HTML file matches the project's existing pattern (see `food/index.html`) and avoids over-engineering for a 5-marker page.

---

## Task 1: Scaffold the directory and data file

**Files:**
- Create: `catania/monuments.json`
- Create: `catania/images/.gitkeep`

The lat/lng values below are pre-filled with real Catania monument coordinates as a starting point. The user can adjust them and supply actual image files afterwards.

- [ ] **Step 1: Create the images directory placeholder**

```bash
mkdir -p catania/images
touch catania/images/.gitkeep
```

- [ ] **Step 2: Create `catania/monuments.json` with 5 entries**

```json
[
  {
    "name": "Cattedrale di Sant'Agata",
    "lat": 37.5036,
    "lng": 15.0876,
    "image": "images/cattedrale.jpg"
  },
  {
    "name": "Fontana dell'Elefante",
    "lat": 37.5034,
    "lng": 15.0866,
    "image": "images/elefante.jpg"
  },
  {
    "name": "Teatro Massimo Bellini",
    "lat": 37.5044,
    "lng": 15.0907,
    "image": "images/teatro-bellini.jpg"
  },
  {
    "name": "Castello Ursino",
    "lat": 37.4988,
    "lng": 15.0851,
    "image": "images/castello-ursino.jpg"
  },
  {
    "name": "Monastero dei Benedettini",
    "lat": 37.5076,
    "lng": 15.0843,
    "image": "images/monastero-benedettini.jpg"
  }
]
```

- [ ] **Step 3: Verify the file is valid JSON**

Run: `python3 -c "import json; print(len(json.load(open('catania/monuments.json'))))"`
Expected output: `5`

- [ ] **Step 4: Commit checkpoint (manual — ask user first)**

Show the diff, then on approval:

```bash
git add catania/monuments.json catania/images/.gitkeep
git commit -m "catania: add monument data file"
```

---

## Task 2: Create the page skeleton with header chrome

**Files:**
- Create: `catania/index.html`

Builds the page shell with the site header pattern, an empty map container, and the MapLibre GL CSS/JS includes — but no map initialization yet. This task produces a viewable empty page so we can verify the chrome before adding map logic.

- [ ] **Step 1: Create `catania/index.html` with this exact content**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <title>Catania — Monuments Map</title>

    <link href="../assets/img/favicon.png" rel="icon">
    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">

    <style>
        html, body { margin: 0; padding: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        body { display: flex; flex-direction: column; }

        header.page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1.25rem;
            background: #fff;
            border-bottom: 1px solid #e5e7eb;
            z-index: 1;
        }
        header.page-header h1 { margin: 0; font-size: 1.25rem; font-weight: 600; }
        header.page-header a { font-size: 0.9rem; color: #0d6efd; text-decoration: none; }
        header.page-header a:hover { text-decoration: underline; }

        #map { flex: 1 1 auto; width: 100%; }

        .monument-marker {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
            background-size: cover;
            background-position: center;
            background-color: #ddd;
            cursor: pointer;
            transition: transform 120ms ease;
        }
        .monument-marker:hover { transform: scale(1.1); }
    </style>
</head>
<body>

<header class="page-header">
    <h1>Catania</h1>
    <a href="../index.html">&larr; Back to home</a>
</header>

<div id="map"></div>

<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script>
    // Map initialization will be added in Task 3.
</script>

</body>
</html>
```

- [ ] **Step 2: Verify the page loads**

Run from repo root: `python3 -m http.server 8000` (in a separate terminal, or with `&`).
Open `http://localhost:8000/catania/` in a browser.

Expected:
- Page title in tab: "Catania — Monuments Map"
- White header bar at top with "Catania" on the left and "← Back to home" on the right
- Rest of the viewport is empty (white)
- No console errors

- [ ] **Step 3: Commit checkpoint (manual — ask user first)**

```bash
git add catania/index.html
git commit -m "catania: add page skeleton with header chrome"
```

---

## Task 3: Initialize the MapLibre map

**Files:**
- Modify: `catania/index.html` (replace the placeholder `<script>` block)

Adds map initialization with OpenFreeMap tiles, Catania-centered view, zoom limits, and pan bounds. After this task the map is visible and interactive but has no markers yet.

- [ ] **Step 1: Replace the inline script with map initialization**

Find this in `catania/index.html`:

```html
<script>
    // Map initialization will be added in Task 3.
</script>
```

Replace with:

```html
<script>
    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/liberty',
        center: [15.0830, 37.5079],
        zoom: 13,
        minZoom: 12,
        maxZoom: 17,
        maxBounds: [[14.97, 37.44], [15.18, 37.56]]
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');
</script>
```

- [ ] **Step 2: Verify the map renders**

Reload `http://localhost:8000/catania/` in the browser.

Expected:
- Map of Catania visible filling the viewport below the header
- Streets, building footprints, labels rendered
- Zoom in/out buttons in the top-right
- Mouse wheel zoom works, but cannot zoom out past whole-city view (minZoom 12) or in past street level (maxZoom 17)
- Cannot pan far away from Catania (hits invisible bounds wall)
- "© OpenStreetMap" / "OpenFreeMap" attribution visible in the bottom-right corner
- No console errors

If the map fails to load: open DevTools Network tab and check the request to `tiles.openfreemap.org` — if blocked, double-check the style URL is exactly `https://tiles.openfreemap.org/styles/liberty`.

- [ ] **Step 3: Commit checkpoint (manual — ask user first)**

```bash
git add catania/index.html
git commit -m "catania: initialize MapLibre map with OpenFreeMap tiles"
```

---

## Task 4: Load monument data and render markers

**Files:**
- Modify: `catania/index.html` (extend the `<script>` block)

Fetches `monuments.json` and creates one constant-size HTML marker per monument. No click handler yet — that comes in Task 5. Markers will look like grey circles since we have no images yet, which is fine for verifying placement.

- [ ] **Step 1: Append marker-rendering code to the existing script**

Inside the `<script>` block, after the `map.addControl(...)` line, append:

```javascript
    map.on('load', async () => {
        try {
            const response = await fetch('monuments.json');
            if (!response.ok) throw new Error('Failed to load monuments.json: ' + response.status);
            const monuments = await response.json();

            for (const monument of monuments) {
                const el = document.createElement('div');
                el.className = 'monument-marker';
                el.title = monument.name;
                el.style.backgroundImage = `url("${monument.image}")`;

                new maplibregl.Marker({ element: el })
                    .setLngLat([monument.lng, monument.lat])
                    .addTo(map);
            }
        } catch (err) {
            console.error('Could not load monuments:', err);
        }
    });
```

- [ ] **Step 2: Verify the markers appear**

Reload `http://localhost:8000/catania/`.

Expected:
- 5 circular markers visible on the map at distinct Catania locations
- Each marker is ~50px, white border, drop shadow
- Markers do NOT scale when you zoom in/out (constant pixel size)
- Hovering a marker shows the monument name as a browser tooltip
- The marker scales up slightly (1.1x) on hover (CSS transition)
- Since image files don't exist yet, marker backgrounds are plain grey (`#ddd` fallback) — this is expected
- No console errors related to JSON loading

If markers don't appear: open DevTools Console and look for fetch errors. The most common cause is opening the page via `file://` instead of `http://localhost:8000/`.

- [ ] **Step 3: Commit checkpoint (manual — ask user first)**

```bash
git add catania/index.html
git commit -m "catania: render monument markers from JSON"
```

---

## Task 5: Wire the click-to-Google-Maps handler

**Files:**
- Modify: `catania/index.html` (extend the marker-creation loop inside the `map.on('load', ...)` callback)

Adds a click listener on each marker element that opens Google Maps in a new tab pointing at the monument's coordinates.

- [ ] **Step 1: Add the click handler inside the marker loop**

Find this block (added in Task 4):

```javascript
            for (const monument of monuments) {
                const el = document.createElement('div');
                el.className = 'monument-marker';
                el.title = monument.name;
                el.style.backgroundImage = `url("${monument.image}")`;

                new maplibregl.Marker({ element: el })
                    .setLngLat([monument.lng, monument.lat])
                    .addTo(map);
            }
```

Replace with:

```javascript
            for (const monument of monuments) {
                const el = document.createElement('div');
                el.className = 'monument-marker';
                el.title = monument.name;
                el.style.backgroundImage = `url("${monument.image}")`;
                el.addEventListener('click', () => {
                    const url = `https://www.google.com/maps/search/?api=1&query=${monument.lat},${monument.lng}`;
                    window.open(url, '_blank', 'noopener');
                });

                new maplibregl.Marker({ element: el })
                    .setLngLat([monument.lng, monument.lat])
                    .addTo(map);
            }
```

- [ ] **Step 2: Verify clicks open Google Maps**

Reload `http://localhost:8000/catania/`.

Expected:
- Clicking any marker opens a new tab to `https://www.google.com/maps/search/?api=1&query=<lat>,<lng>`
- Google Maps shows the location pinned at the monument's coordinates
- Browser does not navigate away from the Catania page
- No console errors

Test all 5 markers to confirm each opens its own coordinates (a quick spot-check on at least 2 of them is fine).

- [ ] **Step 3: Commit checkpoint (manual — ask user first)**

```bash
git add catania/index.html
git commit -m "catania: open Google Maps on marker click"
```

---

## Task 6: User integration — drop in the real images

**Files:**
- Add: `catania/images/cattedrale.jpg`, `catania/images/elefante.jpg`, `catania/images/teatro-bellini.jpg`, `catania/images/castello-ursino.jpg`, `catania/images/monastero-benedettini.jpg`
- Possibly modify: `catania/monuments.json` if the user has different image filenames or wants different monuments

This task is performed by the user (or with the user) — the engineer cannot complete it alone because the image files are external inputs.

- [ ] **Step 1: Receive images from the user**

Ask the user for the 5 monument images. Confirm:
- File names — do they match the paths in `monuments.json`? If not, either rename the files or update `monuments.json`.
- Image dimensions — anything roughly square works since the marker is a 50px circle. Source images can be any reasonable size; the browser will scale via `background-size: cover`. Recommend ~200×200px or larger for crisp rendering on Retina screens.
- File format — `.jpg` is assumed; if the user has `.png` or `.webp`, update the paths in `monuments.json` accordingly.

- [ ] **Step 2: Place the images**

Copy the user's files into `catania/images/` using the filenames referenced in `monuments.json` (or update `monuments.json` to match).

- [ ] **Step 3: If a monument's name or location should change, edit `monuments.json`**

For each monument the user wants to swap or relocate, update its `name`, `lat`, `lng`, and `image` fields in `monuments.json`. Verify with:

```bash
python3 -c "import json; print(json.load(open('catania/monuments.json')))"
```

- [ ] **Step 4: Verify the final result**

Reload `http://localhost:8000/catania/`.

Expected:
- All 5 markers show their actual monument photographs as thumbnails
- Each marker is positioned at its real location
- Clicking each marker opens Google Maps at the correct coordinates
- Hover shows the right name
- No console errors

- [ ] **Step 5: Final commit (manual — ask user first)**

```bash
git add catania/images/ catania/monuments.json
git commit -m "catania: add monument images"
```

---

## Acceptance criteria

After all tasks complete, the page at `http://localhost:8000/catania/` (and at `https://danilotif.github.io/catania/` once deployed) must:

- Load a real-world map of Catania centered on the city
- Show 5 circular monument thumbnails at real geographic locations
- Restrict zoom to a useful city-scale range (12–17)
- Restrict pan to roughly the Catania metro area
- Open Google Maps in a new tab on marker click, pointing at the monument's coordinates
- Show the OSM/OpenFreeMap attribution in the corner
- Have no console errors
- Match the look of other sub-pages (favicon, header, "Back to home" link)
