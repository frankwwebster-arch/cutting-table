#!/usr/bin/env python3
"""Draw a pretend component sheet, so the tool can be tried without owning
a game — and so this repository never needs anyone else's artwork in it.

It is drawn to be awkward in the one way that matters: the water painted
*inside* an island is the same colour as the flat sheet the island is
printed on. That is the case no colour flood can separate, and the reason
the outlines are drawn by hand. Run the tool with --draft on this sheet
and you can watch the automatic attempt cut the big island in half.

    ./demo/make_demo_sheet.py            # writes demo/demo-sheet.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

DPI = 300
W, H = int(6.0 * DPI), int(8.0 * DPI)

FIELD = (110, 147, 216)      # the flat colour the sheet is printed on
SHALLOW = (150, 196, 240)
SAND = (238, 226, 170)
GRASS = (150, 190, 128)
ROCK = (232, 236, 242)
INK = (38, 46, 70)
CARD = (247, 243, 232)


def blob(cx, cy, r, wobble, points, seed):
    """A closed irregular ring — an island, near enough."""
    rnd = random.Random(seed)
    out = []
    for i in range(points):
        a = i / points * math.tau
        rr = r * (1 + rnd.uniform(-wobble, wobble))
        out.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return out


def smooth(pts, passes=3):
    """Chaikin, so the coastline is a curve and not a cut gem."""
    for _ in range(passes):
        nxt = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            nxt.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            nxt.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        pts = nxt
    return pts


def island(d, cx, cy, r, seed, lagoon=False):
    """Sea, then shore, then land — and for the awkward case, a lagoon of
    the sheet's own colour opening to the sea through a narrow mouth."""
    d.polygon(smooth(blob(cx, cy, r, 0.10, 15, seed)), fill=SHALLOW,
              outline=INK, width=3)
    d.polygon(smooth(blob(cx, cy, r * 0.80, 0.12, 15, seed + 1)), fill=SAND)
    d.polygon(smooth(blob(cx, cy, r * 0.62, 0.16, 15, seed + 2)), fill=GRASS)
    if lagoon:
        # the killer: field-coloured water inside the piece, with a mouth
        d.polygon(smooth(blob(cx + r * 0.12, cy, r * 0.34, 0.18, 13, seed + 3)),
                  fill=FIELD)
        d.polygon([(cx + r * 0.3, cy - r * 0.16), (cx + r * 1.1, cy - r * 0.30),
                   (cx + r * 1.1, cy + r * 0.30), (cx + r * 0.3, cy + r * 0.16)],
                  fill=FIELD)
    rnd = random.Random(seed + 9)
    for _ in range(14):
        a, rr = rnd.uniform(0, math.tau), rnd.uniform(0.15, 0.55) * r
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        s = rnd.uniform(8, 20)
        d.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)],
                  fill=ROCK, outline=INK)


def counter(d, x, y, w, h, label, tint):
    d.rectangle([x, y, x + w, y + h], fill=tint, outline=INK, width=3)
    d.rectangle([x + 9, y + 9, x + w - 9, y + h - 9], outline=INK, width=1)
    tw = d.textlength(label)
    d.text((x + (w - tw) / 2, y + h / 2 - 6), label, fill=INK)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    im = Image.new("RGB", (W, H), FIELD)
    d = ImageDraw.Draw(im)

    island(d, 620, 620, 460, 11, lagoon=True)      # the awkward one
    island(d, 1230, 1500, 330, 41)

    # a long reef, which the flood does cope with
    d.polygon(smooth(blob(430, 1620, 300, 0.35, 11, 77)), fill=SHALLOW,
              outline=INK, width=3)

    # a ring of rock round a pool
    d.ellipse([1050, 300, 1600, 850], fill=SHALLOW, outline=INK, width=3)
    for k in range(7):
        f = 1 - k / 8.0
        d.ellipse([1050 + 275 * (1 - f), 300 + 275 * (1 - f),
                   1600 - 275 * (1 - f), 850 - 275 * (1 - f)],
                  outline=(70 + k * 12, 110 + k * 14, 180 + k * 8), width=6)

    # counters, printed on a regular pitch with no gutters — the case the
    # array tool is for
    labels = ["SUNK", "BLAZE", "CREW", "ADRIFT", "TAKEN", "AGROUND"]
    tints = [(226, 122, 118), (243, 206, 128), (168, 208, 168),
             (198, 190, 226), (232, 190, 150), (170, 206, 226)]
    cw, ch = 260, 260
    for row in range(3):
        for col in range(6):
            counter(d, 120 + col * cw, 2050 + row * ch, cw, ch,
                    labels[(row + col) % 6], tints[(row * 2 + col) % 6])

    d.text((40, H - 46), "The Cutting Table — demonstration sheet, not a "
                         "real game", fill=(60, 80, 130))
    im = im.filter(ImageFilter.GaussianBlur(0.4))    # a little press softness
    out = os.path.join(here, "demo-sheet.png")
    im.save(out, dpi=(DPI, DPI))
    print("wrote %s  %d x %d px  %.0f x %.0f in at %ddpi"
          % (out, W, H, W / DPI, H / DPI, DPI))


if __name__ == "__main__":
    main()
