#!/usr/bin/env python3
"""Cutting the pieces out, once their outlines are drawn.

Reads a sheet image and the mask layer exported from the Cutting Table —
one flat colour per piece on transparency, at the sheet's own pixel size
— and writes each piece to its own PNG at full resolution, with a
smoothed, slightly bitten-in edge so the printed die-cut line cannot show
on the finished piece.

    ./cut.py --sheet sheets/core-05.png --mask masks/core-05.png --out cut/

Scale is carried by the recorded inches in the manifest it writes, not by
pixel count, so nothing is ever downsampled.

Needs numpy and Pillow.
"""
import argparse
import json
import os

import numpy as np
from PIL import Image, ImageFilter

import sheets
from sheets import (DPI, BG_TOLERANCE, WHITE, MIN_PIECE_IN, shift_and,
                    shift_or, label)

Image.MAX_IMAGE_PIXELS = None

# Per piece.
#   blur   how much the outline is smoothed
#   bite   how far inside the drawn outline the cut lands, as insurance
#          against the printed die-cut line showing on the finished piece
#   score  darkness of a scored line round the edge, the look of a piece
#          pushed out of the sheet. 0 leaves the edge clean
#   snap   how far to hunt inwards for the real printed edge. Off by
#          default: a hand-drawn outline is taken as the truth
DEFAULTS = {"blur": 3.0, "bite": 3.0, "score": 0.0, "score_px": 3.0,
            "snap": 0, "snap_margin": 6, "line": 12}

def hairline(rgb, strength):
    """The printed die-cut line: a fine dark hairline on lighter ground.

    A morphological black-hat finds it — close the greyscale image with a
    kernel wider than the line, and anything the closing filled in was a
    thin dark mark. Broad dark artwork is not filled, so it is not picked
    up. The line breaks wherever it crosses dark painting, which is why it
    cannot be traced as a curve; used locally, in a band around an outline
    that is already known, the breaks do not matter."""
    g = Image.fromarray(rgb).convert("L")
    closed = g.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    black = np.asarray(closed).astype(np.int16) - np.asarray(g).astype(np.int16)
    return black >= strength


def snap_to_cut(mask, field, cutline, seed, creep, margin):
    """Shrink a hand-drawn outline onto the printed die-cut line.

    The drawn shape only has to be generous and roughly right. From just
    outside it, creep inwards across anything that is still the flat sheet
    colour — that is the spill, where the shape overshot the piece — and
    stop at the first sign of the die cut. Two signals stop it, and either
    alone is enough: the printed hairline, and the step in colour where the
    sheet ends and the piece's painted sea begins. That is why neither
    signal has to be complete.

    The creep is capped, so where both signals fail the shape still holds
    the line and only a little is lost. Whatever the creep reached is then
    widened by `margin` before being cut away, which takes the hairline
    itself off the piece — it is the cut mark, and it is unattractive."""
    if creep <= 0:
        return mask
    inner = mask
    for _ in range(creep):
        inner = shift_and(inner)
    allowed = mask & ~inner & field & ~cutline

    grown = seed & mask
    for _ in range(creep * 2):
        nxt = shift_or(grown) & allowed
        nxt |= grown
        if nxt.sum() == grown.sum():
            break
        grown = nxt
    for _ in range(margin):
        grown = shift_or(grown)

    out = mask & ~grown
    lab, n = label(out)
    if n > 1:                      # keep the body, drop anything cut adrift
        sizes = np.bincount(lab.reshape(-1), minlength=n + 1)
        sizes[0] = 0
        out = lab == int(np.argmax(sizes))
    return out


def smooth_alpha(mask, blur, bite):
    """Turn a ragged pixel mask into an organic outline, pulled in by
    `bite` pixels. Blurring and re-thresholding rounds the staircase off;
    raising the threshold shrinks the shape evenly in every direction."""
    img = Image.fromarray((mask * 255).astype(np.uint8))
    soft = np.asarray(img.filter(ImageFilter.GaussianBlur(blur))).astype(np.float32)
    level = 128.0 + min(120.0, bite * (128.0 / max(blur, 1.0)) * 0.55)
    alpha = np.clip((soft - level) * (255.0 / 40.0) + 128.0, 0, 255)
    return alpha, soft, level


def cut(rgb, mask, box, opts):
    x0, y0, x1, y1 = box
    pad = int(opts["blur"] * 3 + opts["bite"] + 8)
    x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
    x1 = min(rgb.shape[1], x1 + pad); y1 = min(rgb.shape[0], y1 + pad)
    sub = rgb[y0:y1, x0:x1]
    m = mask[y0:y1, x0:x1]
    alpha, soft, level = smooth_alpha(m, opts["blur"], opts["bite"])
    out = sub.astype(np.float32).copy()
    if opts["score"] > 0 and opts["score_px"] > 0:
        # a thin ring just inside the new outline, measured in pixels rather
        # than in blur levels, which do not fall off linearly near the middle
        inside = soft >= level
        eroded = inside
        for _ in range(int(round(opts["score_px"]))):
            eroded = shift_and(eroded)
        out[inside & ~eroded] *= (1.0 - opts["score"])
    rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), alpha.astype(np.uint8)])
    im = Image.fromarray(rgba, "RGBA")
    return im.crop(im.getbbox() or (0, 0, im.width, im.height))


def snap_local(mask, box, field, cutline, seed, opts):
    """Run the die-cut snap on the piece's own corner of the sheet."""
    h, w = mask.shape
    pad = int(opts["snap"] + opts["snap_margin"] + 8)
    x0 = max(0, box[0] - pad); y0 = max(0, box[1] - pad)
    x1 = min(w, box[2] + pad); y1 = min(h, box[3] + pad)
    sub = snap_to_cut(mask[y0:y1, x0:x1], field[y0:y1, x0:x1],
                      cutline[y0:y1, x0:x1], seed[y0:y1, x0:x1],
                      int(opts["snap"]), int(opts["snap_margin"]))
    out = np.zeros((h, w), bool)
    out[y0:y1, x0:x1] = sub
    ys, xs = np.nonzero(sub)
    if not len(ys):
        return mask, box
    return out, (x0 + int(xs.min()), y0 + int(ys.min()),
                 x0 + int(xs.max()) + 1, y0 + int(ys.max()) + 1)


def cut_sheet(sheet_path, mask_path, out_dir, prefix=None, overrides=None):
    """Every piece on one sheet, cut to the mask, at full resolution."""
    rgb = np.asarray(Image.open(sheet_path).convert("RGB"))
    h, w, _ = rgb.shape
    stem = prefix or os.path.splitext(os.path.basename(sheet_path))[0]

    im = Image.open(mask_path).convert("RGBA")
    if im.size != (w, h):
        print("   mask is %d x %d, sheet is %d x %d — scaling the outline"
              % (im.width, im.height, w, h))
        soft = Image.fromarray(
            (np.asarray(im)[:, :, 3] > 128).astype(np.uint8) * 255)
        ink = np.asarray(soft.resize((w, h), Image.BILINEAR)) >= 128
        colour = np.asarray(Image.fromarray(np.asarray(im)[:, :, :3])
                            .resize((w, h), Image.NEAREST))
    else:
        a = np.asarray(im)
        ink = a[:, :, 3] > 128
        colour = a[:, :, :3]

    lab, n = sheets.label_shapes(ink, colour)
    pieces = sheets.keep(lab, n, (h, w))
    pieces.sort(key=lambda p: (p["box"][1] // (DPI // 2), p["box"][0]))
    os.makedirs(out_dir, exist_ok=True)
    print("%s — %d pieces" % (stem, len(pieces)))

    made = []
    for idx, p in enumerate(pieces):
        name = "%s_%02d" % (stem, idx)
        opts = dict(DEFAULTS)
        opts.update((overrides or {}).get(name, {}))
        if opts["snap"] > 0:
            bg = sheets.flat_colour(rgb)
            q = rgb.astype(np.int16)
            field = (((q - bg) ** 2).sum(axis=2) <= BG_TOLERANCE ** 2) | \
                    ((q[:, :, 0] >= WHITE) & (q[:, :, 1] >= WHITE) &
                     (q[:, :, 2] >= WHITE))
            drawn = np.zeros((h, w), bool)
            for o in pieces:
                drawn |= o["mask"]
            seed = shift_or(sheets.outside(field, drawn))
            p["mask"], p["box"] = snap_local(p["mask"], p["box"], field,
                                             hairline(rgb, opts["line"]),
                                             seed, opts)
        piece = cut(rgb, p["mask"], p["box"], opts)
        piece.save(os.path.join(out_dir, name + ".png"))
        print("   %-20s %5d x %5d px  %5.2f x %5.2f in"
              % (name, piece.width, piece.height,
                 piece.width / DPI, piece.height / DPI))
        made.append({"id": name, "image": name + ".png",
                     "width_inches": round(piece.width / DPI, 3),
                     "height_inches": round(piece.height / DPI, 3)})
    return made


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sheet", required=True, help="the printed sheet image")
    ap.add_argument("--mask", required=True,
                    help="the mask layer exported from the Cutting Table")
    ap.add_argument("--out", default="cut", help="where the pieces go")
    ap.add_argument("--prefix", help="what to call them")
    args = ap.parse_args()

    made = cut_sheet(args.sheet, args.mask, args.out, args.prefix)
    # the sizes are the point: a piece is used at its real printed size,
    # never at whatever pixel count it happens to have
    manifest = os.path.join(args.out, "pieces.json")
    have = []
    if os.path.exists(manifest):
        with open(manifest) as fh:
            have = json.load(fh).get("pieces", [])
    ids = set(p["id"] for p in made)
    have = [p for p in have if p["id"] not in ids] + made
    with open(manifest, "w") as fh:
        json.dump({"dpi": DPI, "pieces": have}, fh, indent=1)
    print("   -> %s (%d pieces)" % (manifest, len(have)))


if __name__ == "__main__":
    main()
