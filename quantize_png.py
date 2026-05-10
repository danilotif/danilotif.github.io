#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=10.0", "numpy>=1.24", "scipy>=1.10"]
# ///
"""Quantize PNG colors to shrink AI-generated cartoon images, preserving alpha.

Optional --remove-bg first chroma-keys a background color (default pure green
#00ff00) to fully transparent before quantization, useful for AI-generated
images on a green-screen backdrop.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import label


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    s = hex_color.lstrip("#")
    if len(s) != 6:
        raise ValueError(f"expected #rrggbb, got {hex_color!r}")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def infer_background_color(img: Image.Image) -> tuple[int, int, int] | None:
    """Most common opaque RGB along the 1-pixel border of the image."""
    arr = np.array(img)  # H x W x 4 (RGBA)
    if arr.shape[0] < 2 or arr.shape[1] < 2:
        return None
    border = np.concatenate([
        arr[0, :, :],
        arr[-1, :, :],
        arr[1:-1, 0, :],
        arr[1:-1, -1, :],
    ], axis=0)  # N x 4
    opaque = border[border[:, 3] > 0]
    if opaque.size == 0:
        return None
    rgb = opaque[:, :3].astype(np.uint32)
    encoded = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
    vals, counts = np.unique(encoded, return_counts=True)
    top = int(vals[counts.argmax()])
    return (top >> 16) & 0xff, (top >> 8) & 0xff, top & 0xff


def remove_background(img: Image.Image, hex_color: str, tolerance: int) -> tuple[Image.Image, int, int]:
    target = np.array(hex_to_rgb(hex_color), dtype=np.int16)
    arr = np.array(img, dtype=np.uint8)  # H x W x 4
    rgb = arr[..., :3].astype(np.int16)

    if tolerance <= 0:
        match = np.all(rgb == target, axis=-1)
    else:
        diff = rgb - target
        match = np.sum(diff * diff, axis=-1) <= tolerance * tolerance

    # Flood-fill from the image border: only matched pixels that are connected
    # (4-neighbour) to the border get keyed out. This preserves interior pixels
    # that happen to be close to the background colour (e.g. a green field).
    structure = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    labeled, _ = label(match, structure=structure)
    border_labels = np.unique(np.concatenate([
        labeled[0, :], labeled[-1, :], labeled[:, 0], labeled[:, -1],
    ]))
    border_labels = border_labels[border_labels > 0]
    flood = np.isin(labeled, border_labels)

    matched = int(flood.sum())
    arr[flood, 3] = 0
    return Image.fromarray(arr, mode="RGBA"), matched, arr.shape[0] * arr.shape[1]


def quantize_image(img: Image.Image, colors: int, dither: bool) -> Image.Image:
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    try:
        # libimagequant: same engine as pngquant, alpha-aware, best quality/size.
        return img.quantize(colors=colors, method=Image.Quantize.LIBIMAGEQUANT, dither=dither_mode)
    except ValueError:
        # Fallback: FASTOCTREE is the only built-in method that handles alpha.
        return img.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=dither_mode)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", type=Path, help="Input PNG")
    p.add_argument("-o", "--output", type=Path, help="Output PNG (default: <input>-q<colors>.png)")
    p.add_argument("-c", "--colors", type=int, default=128,
                   help="Max palette colors, 2-256 (default: 128)")
    p.add_argument("--no-dither", action="store_true", help="Disable Floyd-Steinberg dithering")
    p.add_argument("--remove-bg", action="store_true",
                   help="Replace --bg-color pixels with full transparency before quantization")
    p.add_argument("--bg-color", default=None,
                   help="Background color to remove as #rrggbb (default: auto-detect from border pixels)")
    p.add_argument("--bg-tolerance", type=int, default=None,
                   help="Match radius in RGB units, 0=exact (default: 30 with auto-detect, 0 with explicit --bg-color)")
    args = p.parse_args()

    if not args.input.is_file():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not 2 <= args.colors <= 256:
        print("error: --colors must be between 2 and 256", file=sys.stderr)
        return 1

    img = Image.open(args.input)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    if args.remove_bg:
        auto = args.bg_color is None
        if auto:
            inferred = infer_background_color(img)
            if inferred is None:
                print("error: could not infer background color (border is fully transparent); "
                      "pass --bg-color explicitly", file=sys.stderr)
                return 1
            bg_hex = rgb_to_hex(inferred)
            print(f"auto-detected background: {bg_hex} (mode of border pixels)")
        else:
            bg_hex = args.bg_color
        tol = args.bg_tolerance if args.bg_tolerance is not None else (30 if auto else 0)
        img, matched, total = remove_background(img, bg_hex, tol)
        pct_matched = matched / total * 100 if total else 0
        print(f"chroma-key {bg_hex} (tol={tol}): "
              f"{matched:,}/{total:,} pixels → transparent ({pct_matched:.1f}%)")
        if pct_matched < 1:
            print("  hint: bump --bg-tolerance higher to catch noisier backgrounds",
                  file=sys.stderr)

    quantized = quantize_image(img, args.colors, dither=not args.no_dither)

    out = args.output or args.input.with_name(f"{args.input.stem}-q{args.colors}.png")
    quantized.save(out, format="PNG", optimize=True)

    before = args.input.stat().st_size
    after = out.stat().st_size
    pct = (1 - after / before) * 100 if before else 0
    label = "smaller" if pct >= 0 else "larger"
    print(f"{args.input.name}: {before:,} → {after:,} bytes ({abs(pct):.1f}% {label})")
    print(f"wrote: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
