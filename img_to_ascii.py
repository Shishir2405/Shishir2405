#!/usr/bin/env python3
"""
img_to_ascii.py — turn a photo/avatar into a COLORED neofetch-style ASCII portrait.

Writes portrait.json:  {"cols":C,"rows":R,"cells":[[ null | [char,"#rrggbb"], ... ], ...]}
  - null  = background (rendered as a space, in both themes)
  - each foreground cell carries a glyph (density from luminance) and a color
    sampled from the image, snapped to a small palette and brightness-clamped so
    it reads on BOTH a dark (#0d1117) and a light (#ffffff) background.

Usage:
    python3 img_to_ascii.py avatar.png --mask avatar.png
    python3 img_to_ascii.py avatar.png --mask avatar.png --cols 46 --rows 26 --colors 16
"""
import argparse, colorsys, json
from PIL import Image

RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
CELL_W, CELL_H = 5.4, 10.0           # matches the portrait font-size (9px) in generate_svg
DARK_LO, DARK_HI = 96, 236          # visible band on a DARK background  (#0d1117)
LIGHT_LO, LIGHT_HI = 28, 168        # visible band on a LIGHT background (#ffffff)


def saturate(rgb, factor=1.3):
    r, g, b = (c / 255 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(h, min(1.0, s * factor), v)
    return (int(r * 255), int(g * 255), int(b * 255))


def clamp_range(rgb, lo, hi):
    """Scale a color's luminance into [lo, hi], preserving hue."""
    r, g, b = rgb
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 1:
        return (lo, lo, lo)
    f = max(lo, min(hi, lum)) / lum
    return tuple(min(255, int(c * f)) for c in (r, g, b))


def hexof(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def aspect_crop(img, target_ar, ybias):
    w, h = img.size
    if w / h > target_ar:
        nw = int(h * target_ar); left = (w - nw) // 2
        return img.crop((left, 0, left + nw, h))
    nh = int(w / target_ar); top = int((h - nh) * ybias)
    return img.crop((0, top, w, top + nh))


def build(image, mask_path, cols, rows, ybias, ncolors, floor):
    src = Image.open(image).convert("RGBA")
    rgb = src.convert("RGB")
    gray = src.convert("L")
    mask = (Image.open(mask_path).convert("RGBA").getchannel("A")
            if mask_path else Image.new("L", src.size, 255)).resize(src.size)

    target_ar = (cols * CELL_W) / (rows * CELL_H)
    rgb = aspect_crop(rgb, target_ar, ybias)
    gray = aspect_crop(gray, target_ar, ybias)
    mask = aspect_crop(mask, target_ar, ybias)

    # per-cell averaged color -> snap to a small palette for clean, retro color runs
    small = rgb.resize((cols, rows), Image.LANCZOS)
    pal = small.quantize(colors=ncolors, method=Image.MEDIANCUT).convert("RGB")
    g = gray.resize((cols, rows), Image.LANCZOS)
    m = mask.resize((cols, rows), Image.LANCZOS)
    pp, gp, mp = pal.load(), g.load(), m.load()
    L = len(RAMP) - 1

    cells = []
    for y in range(rows):
        row = []
        for x in range(cols):
            if mp[x, y] < 110:
                row.append(None); continue
            lum = gp[x, y] / 255.0
            ink = floor + (1 - floor) * (1 - lum)      # darker pixel -> denser glyph
            ch = RAMP[max(round(ink * L), round(floor * L))]  # never blank a fg cell
            base = saturate(pp[x, y])
            row.append([ch,
                        hexof(clamp_range(base, DARK_LO, DARK_HI)),    # dark-theme color
                        hexof(clamp_range(base, LIGHT_LO, LIGHT_HI))]) # light-theme color
        cells.append(row)
    return {"cols": cols, "rows": rows, "cells": cells}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--mask", default=None)
    ap.add_argument("--cols", type=int, default=78)
    ap.add_argument("--rows", type=int, default=46)
    ap.add_argument("--ybias", type=float, default=0.3)
    ap.add_argument("--colors", type=int, default=20, help="palette size for color snapping")
    ap.add_argument("--floor", type=float, default=0.35, help="min glyph density for color fill")
    a = ap.parse_args()

    data = build(a.image, a.mask, a.cols, a.rows, a.ybias, a.colors, a.floor)
    with open("portrait.json", "w") as f:
        json.dump(data, f)

    # console preview (mono)
    for row in data["cells"]:
        print("".join(c[0] if c else " " for c in row).rstrip())
    print(f"\nwrote portrait.json ({a.cols}x{a.rows}, {a.colors} colors)")


if __name__ == "__main__":
    main()
