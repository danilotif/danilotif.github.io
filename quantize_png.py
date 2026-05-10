#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["Pillow>=10.0"]
# ///
"""Quantize PNG colors to shrink AI-generated cartoon images, preserving alpha."""
import argparse
import sys
from pathlib import Path

from PIL import Image


def quantize_png(src: Path, dst: Path, colors: int, dither: bool) -> tuple[int, int]:
    img = Image.open(src)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE

    try:
        # libimagequant: same engine as pngquant, alpha-aware, best quality/size.
        quantized = img.quantize(
            colors=colors,
            method=Image.Quantize.LIBIMAGEQUANT,
            dither=dither_mode,
        )
    except ValueError:
        # Fallback: FASTOCTREE is the only built-in method that handles alpha.
        quantized = img.quantize(
            colors=colors,
            method=Image.Quantize.FASTOCTREE,
            dither=dither_mode,
        )

    quantized.save(dst, format="PNG", optimize=True)
    return src.stat().st_size, dst.stat().st_size


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path, help="Input PNG")
    p.add_argument("-o", "--output", type=Path, help="Output PNG (default: <input>-q.png)")
    p.add_argument("-c", "--colors", type=int, default=128,
                   help="Max palette colors, 2-256 (default: 128)")
    p.add_argument("--no-dither", action="store_true", help="Disable Floyd-Steinberg dithering")
    args = p.parse_args()

    if not args.input.is_file():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not 2 <= args.colors <= 256:
        print("error: --colors must be between 2 and 256", file=sys.stderr)
        return 1

    out = args.output or args.input.with_name(f"{args.input.stem}-q{args.colors}.png")
    before, after = quantize_png(args.input, out, args.colors, dither=not args.no_dither)
    pct = (1 - after / before) * 100 if before else 0
    label = "smaller" if pct >= 0 else "larger"
    print(f"{args.input.name}: {before:,} → {after:,} bytes ({abs(pct):.1f}% {label})")
    print(f"wrote: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
