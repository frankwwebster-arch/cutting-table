"""⚠️ NAMES MUST FOLLOW THEIR PIECES WHEN A SHEET IS CUT AGAIN.

This is the most delicate code in the room and for a long time nothing
exercised it at all.

The trouble is that pieces are NUMBERED IN READING ORDER. Outline one more
piece near the top of a sheet and every piece below it shifts up a number,
so a name given to `..._03` would quietly land on what used to be `..._02`
— a different counter, with the wrong name on it, and nothing to say so.
`cut_sheet()` guards against that by matching each new piece to an old one
by how much their boxes overlap, and rewriting the manifest's keys to suit.

Run through check/check.sh. It builds its own throwaway game in a temporary
folder — NEVER point this at a real project; cutting writes to the manifest,
and the manifest is one of the two things that cannot be rebuilt.
"""
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cutting_room as room                                        # noqa: E402

DPI = 300
done = []


def check(what, right, saw=None):
    done.append(right)
    print(("  ok   " if right else "  WRONG ") + what +
          ("" if saw is None else "   — saw " + json.dumps(saw, ensure_ascii=False)))


def box(x, y, w, h):
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def bed(where, boxes):
    """A one-sheet game with the given outlines already on it."""
    d = os.path.join(where, "recut")
    os.makedirs(os.path.join(d, "sheets"), exist_ok=True)
    shutil.copyfile("demo/demo-sheet.png",
                    os.path.join(d, "sheets", "recut-sheets-01.png"))
    json.dump({"id": "recut", "name": "The Re-cut Bench", "game": "nothing real",
               "dpi": DPI, "notes": "", "paths": {}, "hooks": [],
               "sheets": [{"id": "recut-sheets-01", "label": "recut-sheets p.1",
                           "name": "a pretend sheet", "w": 1800, "h": 2400}]},
              open(os.path.join(d, "project.json"), "w"), indent=1)
    outline(d, boxes)
    return d


def outline(d, boxes):
    json.dump({"tool": "cutting-table", "version": 2,
               "sheets": {"recut-sheets-01": {
                   "pieces": [{"pts": b, "ink": i % 6, "name": ""}
                              for i, b in enumerate(boxes)]}}},
              open(os.path.join(d, "outlines.json"), "w"), indent=1)


def cut(d):
    pr = room.Project(d)
    made = room.cut_sheet(pr, "recut-sheets-01")["made"]
    return pr, made


def names_by_box(d):
    """What each cut piece is called, filed under where it sits on the sheet
    — which is the only identity that survives a renumbering."""
    pr = room.Project(d)
    idx = pr.index().get("pieces", {})
    man = pr.manifest().get("pieces", {})
    out = {}
    for stem, v in idx.items():
        b = v.get("box")
        if not b:
            continue
        out[b[1] // 100] = (man.get(stem) or {}).get("name", "")
    return out


def name_them(d, names):
    pr = room.Project(d)
    man = pr.manifest()
    stems = sorted(pr.index().get("pieces", {}))
    for stem, nm in zip(stems, names):
        man["pieces"].setdefault(stem, {})["name"] = nm
    pr.save_manifest(man)
    return stems


def marks_by_box(d, field):
    "Any field of the manifest, filed under where its piece sits on the sheet."
    pr = room.Project(d)
    idx = pr.index().get("pieces", {})
    man = pr.manifest().get("pieces", {})
    out = {}
    for stem, v in idx.items():
        b = v.get("box")
        if b:
            out[b[1] // 100] = (man.get(stem) or {}).get(field, "")
    return out


# ---------------------------------------------------------------------------

def main():
    tmp = tempfile.mkdtemp(prefix="cutting-recut-")
    try:
        # three pieces down the sheet, named for where they are
        THREE = [box(200, 400, 500, 240), box(200, 900, 500, 240),
                 box(200, 1400, 500, 240)]
        NAMES = ["the one at 400", "the one at 900", "the one at 1400"]

        print("\none more piece outlined ABOVE the others, and cut again")
        d = bed(tmp, THREE)
        cut(d)
        stems = name_them(d, NAMES)
        check("three pieces cut, numbered in reading order", stems == [
            "recut_sheets_p01_00", "recut_sheets_p01_01", "recut_sheets_p01_02"], stems)
        before = names_by_box(d)

        # the new one goes in at the TOP, so every old piece shifts a number
        outline(d, [box(200, 100, 500, 240)] + THREE)
        cut(d)
        after = names_by_box(d)
        check("there are four pieces now", len(after) == 4, sorted(after))
        for y, nm in ((4, "the one at 400"), (9, "the one at 900"), (14, "the one at 1400")):
            check("the piece at %-5s is still called what it was called" % (y * 100),
                  after.get(y) == nm, {"at": y * 100, "now": after.get(y)})
        check("the new piece at the top has no name of its own",
              after.get(1, "") == "", {"now": after.get(1)})

        print("\nthe top piece's outline removed, and cut again")
        d2 = bed(tmp + "/b", [box(200, 100, 500, 240)] + THREE)
        cut(d2)
        name_them(d2, ["the new one at 100"] + NAMES)
        outline(d2, THREE)                       # the top one is taken away
        cut(d2)
        gone = names_by_box(d2)
        check("there are three pieces again", len(gone) == 3, sorted(gone))
        for y, nm in ((4, "the one at 400"), (9, "the one at 900"), (14, "the one at 1400")):
            check("the piece at %-5s survived the removal above it" % (y * 100),
                  gone.get(y) == nm, {"at": y * 100, "now": gone.get(y)})
        # ⚠️ the fault this whole mechanism exists to stop: a name landing on
        # a piece that is not the one it was given to
        check("the removed piece's name did not land on a neighbour",
              "the new one at 100" not in gone.values(),
              {k * 100: v for k, v in sorted(gone.items())})

        print("\na piece moved a little, and one nudged out from under its name")
        d3 = bed(tmp + "/c", THREE)
        cut(d3)
        name_them(d3, NAMES)
        # the middle one is redrawn 30px lower — the same piece, adjusted
        outline(d3, [THREE[0], box(200, 930, 500, 240), THREE[2]])
        cut(d3)
        nudged = names_by_box(d3)
        check("a piece adjusted by a little keeps its name",
              nudged.get(9) == "the one at 900", {"now": nudged.get(9)})

        print("\nthe BOTTOM piece's outline removed, and cut again")
        # ⚠️ This is the case the reading-order match does NOT cover by
        # itself. Take the LAST piece away and every piece above it keeps
        # the number it already had, so nothing needs renaming and the
        # rename map comes out empty — at which point the manifest was not
        # rewritten at all and the dead piece's name stayed in it.
        d4 = bed(tmp + "/d", THREE + [box(200, 1900, 500, 240)])
        cut(d4)
        name_them(d4, NAMES + ["the one at 1900"])
        outline(d4, THREE)                       # the bottom one is taken away
        cut(d4)
        pr4 = room.Project(d4)
        man4 = pr4.manifest().get("pieces", {})
        idx4 = pr4.index().get("pieces", {})
        check("there are three pieces again", len(idx4) == 3, sorted(idx4))
        check("the removed piece's name is not left behind in the manifest",
              set(man4) <= set(idx4), sorted(set(man4) - set(idx4)))

        # ...and what a left-behind name does next: outline something ELSE
        # in that spot and it inherits a name it was never given
        outline(d4, THREE + [box(200, 1900, 500, 240)])
        cut(d4)
        back = names_by_box(d4)
        check("a different piece cut in that spot does NOT inherit the old name",
              back.get(19, "") == "", {"at": 1900, "now": back.get(19)})

        print("\na piece marked as one of several designs of one component")
        # ⭐️ The `alike` mark says "these are the two player markers, or the
        # twelve movement templates — different DESIGNS of one component, keep them
        # all". It is written onto the piece rather than kept in a list of its
        # own for exactly this reason: it has to survive a renumbering the way
        # a name does, or the room starts proposing to bin them again the
        # moment the sheet is cut a second time.
        d5 = bed(tmp + "/e", THREE)
        cut(d5)
        pr5 = room.Project(d5)
        man5 = pr5.manifest()
        for stem in sorted(pr5.index().get("pieces", {})):
            man5["pieces"].setdefault(stem, {})["alike"] = "v-marker"
        pr5.save_manifest(man5)
        outline(d5, [box(200, 100, 500, 240)] + THREE)   # one more above them
        cut(d5)
        marks = marks_by_box(d5, "alike")
        for y in (4, 9, 14):
            check("the variant mark at %-5s came through the renumbering" % (y * 100),
                  marks.get(y) == "v-marker", {"at": y * 100, "now": marks.get(y)})
        check("the new piece above them is not swept into the group",
              marks.get(1, "") == "", {"now": marks.get(1)})

        # ⭐️ AND THE SAME FOR A FLAG THE PERSON HAS ANSWERED. The designer, 24 August
        # 2026, of RUNS OFF THE SHEET: "I don't see a way to remove that flag
        # (because it doesn't matter)." There is one now — and if it did not
        # survive a re-cut, every worry they had already looked at and waved
        # through would come back the next time the sheet was cut, which is
        # the same fault as handing back the duplicates they had just set aside.
        man5 = pr5.manifest()
        for stem in sorted(pr5.index().get("pieces", {})):
            man5["pieces"].setdefault(stem, {})["fine"] = "edge tiny"
        pr5.save_manifest(man5)
        # ⚠️ The top outline goes and one arrives at the BOTTOM, so every
        # piece shifts a number AND the new piece takes the number the last
        # one used to have — which is exactly where a mark would land on a
        # piece it was never given to.
        outline(d5, THREE + [box(200, 1800, 500, 240)])
        cut(d5)
        waved = marks_by_box(d5, "fine")
        for y in (4, 9, 14):
            check("a flag waved through at %-5s stays waved through" % (y * 100),
                  waved.get(y) == "edge tiny", {"at": y * 100, "now": waved.get(y)})
        check("and a piece cut for the first time carries no such answer",
              waved.get(18, "") == "", {"now": waved.get(18)})

        print("\na piece SET ASIDE is moved, never deleted, and stays put")
        # ⭐️ THE DESIGNER: "Binning a piece shouldn't be destructive — it should be
        # merely to hide a piece from the main manifest. eg there are two
        # identical terrain tiles. The game only needs to store one, even though
        # it could be placed twice in an actual game."
        d6 = bed(tmp + "/f", THREE)
        cut(d6)
        name_them(d6, NAMES)
        pr6 = room.Project(d6)
        spare = sorted(pr6.index().get("pieces", {}))[2]        # the one at 1400
        pr6.set_aside([spare], True)
        check("its file left the store, and is not in the hand-over's way",
              not os.path.exists(pr6.piece_path(spare)), spare)
        check("its file is in the spare folder, not deleted",
              os.path.exists(pr6.spare_path(spare)), spare)
        check("the store the game reads no longer offers it",
              spare not in pr6.piece_files(), pr6.piece_files())
        check("the room can still measure it, so it can still be shown",
              (pr6.measure_piece(spare) or {}).get("w_in") is not None)
        check("its name and everything else about it is kept",
              (pr6.manifest()["pieces"].get(spare) or {}).get("name")
              == "the one at 1400",
              pr6.manifest()["pieces"].get(spare))

        # ...and it must not come marching back the next time the sheet is cut
        outline(d6, [box(200, 100, 500, 240)] + THREE)     # one more above them
        cut(d6)
        pr6 = room.Project(d6)
        still = [st for st, v in pr6.manifest().get("pieces", {}).items()
                 if v.get("spare")]
        check("it is still set aside after a re-cut renumbered everything",
              len(still) == 1, still)
        if still:
            check("and its file is still in the spare folder, not the store",
                  os.path.exists(pr6.spare_path(still[0]))
                  and not os.path.exists(pr6.piece_path(still[0])), still[0])
            check("the piece that took its old number is NOT set aside",
                  marks_by_box(d6, "spare").get(14) is True
                  and marks_by_box(d6, "spare").get(9) in ("", None, False),
                  {k * 100: v for k, v in sorted(marks_by_box(d6, "spare").items())})

        # putting it back
        pr6.set_aside(still, False)
        check("putting it back returns the file to the store",
              still and os.path.exists(pr6.piece_path(still[0])), still)
        check("and nothing in the manifest is still marked spare",
              not [v for v in pr6.manifest()["pieces"].values() if v.get("spare")])

        print("\nnothing was left pointing at a piece that is gone")
        pr = room.Project(d2)
        man = set(pr.manifest().get("pieces", {}))
        idx = set(pr.index().get("pieces", {}))
        check("every name in the manifest belongs to a piece that exists",
              man <= idx, sorted(man - idx))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    wrong = [d for d in done if not d]
    print("\n%s" % (("%d of %d checks are WRONG" % (len(wrong), len(done)))
                    if wrong else "all %d checks came out right" % len(done)))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
