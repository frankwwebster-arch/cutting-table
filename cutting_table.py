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
SUGGEST_TOL = sheets.SUGGEST_TOL     # ⚠️ one set of numbers, in sheets.py
SUGGEST_INSET = sheets.SUGGEST_INSET

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


# ⚠️ THE TRACING ITSELF LIVES IN sheets.py, and this file used to carry a
# second copy of it. Two copies of the same arithmetic in the two things that
# draft the same sheets is fault 24 waiting to happen — and it happened the
# moment the tracing was made worth using, because only one of them would have
# been improved.
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

    # ⚠️ ONE COPY OF THE DRAFTING, in sheets.py — the room and this baker draft
    # the same sheets and two copies of it would drift apart (fault 24). It was
    # the TRACING that was shared before; the choosing was still written out
    # twice, so the rule that drops hairline artefacts reached the room alone.
    return sheets.trace_all(lab, n, sx, sy, DPI)


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
             " (%s nodes)" % "/".join(str(len(o["pts"])) for o in suggested)))
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
