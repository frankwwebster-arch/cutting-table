#!/usr/bin/env python3
"""Bake a set of printed component sheets into one self-contained page.

The Cutting Table is where the outlines get drawn. Cutting components off
a printed sheet cannot be done reliably by colour — see cut_terrain.py for
why — so the outline is drawn by hand once, and everything after that is
automatic. This writes a single HTML file with the sheets, the automatic
attempt at each one, and the outlining tool all inside it. Nothing is
fetched over the network, so it works on a train.

What comes back out of it is a MASK LAYER per sheet: each piece filled in
a flat colour on transparency, at the sheet's exact pixel size, which is
what cut_terrain.py reads.

Nothing here knows about any particular game:

    ./cutting_table.py --images scans/*.png --subject "A dungeon game"
    ./cutting_table.py --pdf components.pdf --pages 3,5,7 \\
        --subject "A boxed game · card terrain" --out ~/Desktop/Cutting.html

Needs Pillow and numpy; and pdftoppm (poppler) for --pdf.
"""
import argparse
import base64
import io
import json
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sheets                                               # noqa: E402

Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "cutting_table.tpl.html")
DPI = 300
MIN_PIECE_IN = 0.25
SUGGEST_TOL = 7.0       # sheet px a suggested outline may cut a corner by
SUGGEST_INSET = 6       # sheet px a suggested outline starts inside the edge

DEFAULT_SUBJECT = "Printed card components"
DEFAULT_OUT = os.path.expanduser("~/Desktop/Cutting Table.html")
DRAFT_DIR = "drafts"    # where the colour flood's first attempts are kept


def data_uri(raw, mime):
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))


def render_pdf(pdf, pages, work):
    """Render the wanted pages of a PDF at 300dpi."""
    out = {}
    for page in pages:
        stem = os.path.join(work, "p%02d" % page)
        subprocess.run(["pdftoppm", "-r", str(DPI), "-f", str(page),
                        "-l", str(page), "-png", pdf, stem],
                       check=True, capture_output=True)
        hit = sorted(f for f in os.listdir(work)
                     if f.startswith("p%02d-" % page))
        if hit:
            out[page] = os.path.join(work, hit[0])
    return out


def contour(mask):
    """The outline of a filled shape, as a ring of pixel positions.

    Moore-neighbour tracing: stand on a boundary pixel, and keep turning
    round it until the next boundary pixel is found, taking the direction
    you arrived from as where to start looking. Stops on returning to the
    first pixel the same way it first left it, which is what keeps a shape
    with a narrow neck from being walked twice."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return []
    h, w = mask.shape
    y0 = int(ys.min())
    x0 = int(xs[ys == y0].min())
    step = [(1, 0), (1, 1), (0, 1), (-1, 1),
            (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def on(x, y):
        return 0 <= x < w and 0 <= y < h and mask[y, x]

    start = (x0, y0)
    ring = [start]
    here = start
    back = 4                      # arrived from the west
    limit = 8 * int(mask.sum()) + 64
    for _ in range(limit):
        found = False
        for k in range(1, 9):
            d = (back + k) % 8
            nxt = (here[0] + step[d][0], here[1] + step[d][1])
            if on(nxt[0], nxt[1]):
                back = (d + 4) % 8
                here = nxt
                found = True
                break
        if not found:
            break                 # a single stranded pixel
        if here == start:
            break                 # all the way round
        ring.append(here)
    return ring


def thin(pts, tol):
    """Douglas-Peucker: keep only the points that carry the shape, so what
    comes out is a handful of nodes to drag rather than a traced pixel ring.
    Iterative, because a traced ring runs to thousands of points."""
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    work = [(0, len(pts) - 1)]
    while work:
        lo, hi = work.pop()
        if hi <= lo + 1:
            continue
        ax, ay = pts[lo]
        bx, by = pts[hi]
        vx, vy = bx - ax, by - ay
        L = vx * vx + vy * vy
        worst, at = 0.0, -1
        for i in range(lo + 1, hi):
            px, py = pts[i]
            t = ((px - ax) * vx + (py - ay) * vy) / L if L else 0.0
            t = 0.0 if t < 0 else (1.0 if t > 1 else t)
            d = math.hypot(px - (ax + t * vx), py - (ay + t * vy))
            if d > worst:
                worst, at = d, i
        if worst > tol:
            keep[at] = True
            work.append((lo, at))
            work.append((at, hi))
    return [pts[i] for i in range(len(pts)) if keep[i]]


def outlines_for(sheet_id, w, h):
    """The automatic attempt at this sheet, handed over as outlines with
    nodes on them rather than as a picture — so the first job is correcting
    a shape rather than drawing one."""
    path = None
    for name in ("%s-starter.png" % sheet_id, "%s.png" % sheet_id):
        cand = os.path.join(DRAFT_DIR, name)
        if os.path.exists(cand):
            path = cand
            break
    if not path:
        return []

    im = Image.open(path).convert("RGBA")
    a = np.asarray(im)
    ink = a[:, :, 3] > 128
    lab, n = sheets.label_shapes(ink, a[:, :, :3])
    sx, sy = w / float(im.width), h / float(im.height)
    smallest = (MIN_PIECE_IN * DPI * 0.8) ** 2

    out = []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < smallest:
            continue
        # start a touch inside the printed edge; it is easier to push a node
        # out than to notice one sitting on the cut line
        for _ in range(SUGGEST_INSET):
            m = sheets.shift_and(m)
        if not m.any():
            continue
        ring = contour(m)
        if len(ring) < 12:
            continue
        pts = thin(ring, SUGGEST_TOL)
        if len(pts) < 3:
            continue
        out.append([[round(p[0] * sx, 1), round(p[1] * sy, 1)] for p in pts])
    out.sort(key=lambda p: (min(q[1] for q in p) // (DPI // 2),
                            min(q[0] for q in p)))
    return out


def pack(path, sheet_id, label, name, quality, draft=False):
    im = Image.open(path).convert("RGB")
    if draft:
        # let the colour flood have a go first, so there is something to
        # correct rather than a blank sheet. It is wrong wherever a piece's
        # own painted background matches the sheet — which is the whole
        # reason the outlines are drawn by hand — but it is a start.
        os.makedirs(DRAFT_DIR, exist_ok=True)
        sheets.starter(np.asarray(im),
                       os.path.join(DRAFT_DIR, "%s-starter.png" % sheet_id))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    suggested = outlines_for(sheet_id, im.width, im.height)
    print("   %-10s %5d x %5d px   %.2f MB   %d suggested outlines%s"
          % (label, im.width, im.height, len(buf.getvalue()) / 1e6,
             len(suggested),
             "" if not suggested else
             " (%s nodes)" % "/".join(str(len(o)) for o in suggested)))
    return {
        "id": sheet_id,
        "label": label,
        "name": name,
        "w": im.width,
        "h": im.height,
        "src": data_uri(buf.getvalue(), "image/jpeg"),
        "suggested": suggested,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdf", help="a PDF of component sheets")
    ap.add_argument("--pages", help="which pages of it, e.g. 3,5,7")
    ap.add_argument("--images", nargs="*", help="sheet images instead of a PDF")
    ap.add_argument("--prefix", default="sheet", help="what to name the masks")
    ap.add_argument("--draft", action="store_true",
                    help="draft outlines by colour flood first, to correct")
    ap.add_argument("--subject", default=DEFAULT_SUBJECT,
                    help="shown beside the title")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--quality", type=int, default=82,
                    help="JPEG quality of the baked sheets")
    args = ap.parse_args()

    out = []
    if args.images:
        for i, path in enumerate(args.images):
            stem = os.path.splitext(os.path.basename(path))[0]
            out.append(pack(path, "%s-%02d" % (args.prefix, i + 1),
                            "Sheet %d" % (i + 1), stem, args.quality,
                            args.draft))
    elif args.pdf:
        pdf = args.pdf
        if not args.pages:
            sys.exit("--pages is required with --pdf, e.g. --pages 3,5,7")
        pages = [int(v) for v in args.pages.split(",")]
        if not os.path.exists(pdf):
            sys.exit("no such PDF: %s" % pdf)
        print("rendering %s at %ddpi" % (os.path.basename(pdf), DPI))
        with tempfile.TemporaryDirectory() as work:
            for page, path in sorted(render_pdf(pdf, pages, work).items()):
                out.append(pack(path, "%s-%02d" % (args.prefix, page),
                                "Sheet %d" % page, "", args.quality,
                                args.draft))

    else:
        sys.exit("give it --images FILES or --pdf FILE --pages 3,5,7")
    if not out:
        sys.exit("no sheets to bake")

    with open(TEMPLATE) as fh:
        html = fh.read()
    html = html.replace("/*__SHEETS__*/", json.dumps(out))
    html = html.replace("/*__SUBJECT__*/", args.subject.replace('"', "'"))
    with open(args.out, "w") as fh:
        fh.write(html)
    print("wrote %s  (%.2f MB, %d sheets, opens with no network)"
          % (args.out, os.path.getsize(args.out) / 1e6, len(out)))


if __name__ == "__main__":
    main()
