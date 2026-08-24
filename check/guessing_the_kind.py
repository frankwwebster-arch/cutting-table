"""⭐️ GUESSING WHAT A PIECE IS, FROM ITS PRINTED SIZE AND ITS SHAPE.

The designer, 22 August 2026, having cut a sheet and named it by hand: "naming is
always going to be the fiddly bit here as it will tend to rely on 3rd party
lists etc, or rules manuals which may be tricky to comprehend." Cutting a
sheet is one press; saying what each of two hundred pieces IS is the evening.
So the room offers a kind rather than asking for one — and this is the whole
of what it knows.

⚠️ TWO THINGS ARE BEING CHECKED HERE, AND THE SECOND MATTERS MORE:

  1. that the room recognises the three things it claims to know — a counter,
     a card and a ruler;

  2. ⭐️ that it KEEPS ITS MOUTH SHUT about everything else. A piece the size
     of a page could be a board, a chart, a player mat or the back of the box,
     and a confident wrong answer offered to somebody naming three hundred
     pieces will be accepted without looking. Silence is the right answer far
     more often than any particular kind is, and these checks are mostly here
     to stop a future rule getting greedy.

No browser and no project: `guess_kind` is a measurement and nothing else.
Run through check/check.sh.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cutting_room as room                                        # noqa: E402

done = []


def check(what, right, saw=None):
    done.append(right)
    print(("  ok   " if right else "  WRONG ") + what +
          ("" if saw is None else "   — saw " + json.dumps(saw, ensure_ascii=False)))


def kind_of(w, h, cover=0.99):
    got = room.guess_kind(w, h, cover)
    return got["kind"] if got else None


def main():
    print("the shapes the room is sure about")
    # Card stock is bought, not designed: these sizes are the same in a game
    # about spaceships and a game about farming, which is why they are safe.
    check("a poker card, either way up",
          kind_of(2.5, 3.5) == "card" and kind_of(3.5, 2.5) == "card")
    check("a bridge card, a mini card and a tarot card",
          [kind_of(2.25, 3.5), kind_of(1.75, 2.5), kind_of(2.75, 4.75)] == ["card"] * 3)
    check("a card measured a little short by the scanner is still a card",
          kind_of(2.46, 3.44) == "card", room.guess_kind(2.46, 3.44, 0.99)["why"])
    check("a half-inch counter and a five-eighths counter",
          [kind_of(0.5, 0.5), kind_of(0.63, 0.63)] == ["counter"] * 2)
    check("a counter is not required to be exactly square",
          kind_of(0.6, 0.66) == "counter")
    check("a ruler, and a long thin range stick",
          [kind_of(8.0, 0.6), kind_of(11.0, 1.5)] == ["ruler"] * 2)
    # ⚠️ THIS ONE CAME OFF A REAL GAME. The rule as first written called two
    # TERRAIN TILES rulers: 1.89 x 6.79in, long and thin and entirely innocent —
    # but ragged blobs of terrain filling three quarters of their box, not
    # printed strips. A ruler is SOLID; that is the whole difference.
    check("but a long ragged blob of terrain is not a ruler",
          kind_of(1.893, 6.787, 0.748) is None)
    check("while the real range ruler beside it still is",
          kind_of(1.99, 11.94, 0.989) == "ruler")
    # ⭐️ A game's publisher does not buy card stock off a shelf. Real boxes
    # print cards at 2.54 x 3.80in and stranger sizes still, none of them a
    # standard anybody else uses.
    # A card is a thing held in the hand, so its PROPORTIONS give it away
    # when its measurements do not.
    check("a card of no standard size at all is still offered as a card",
          kind_of(2.543, 3.8) == "card", room.guess_kind(2.543, 3.8, 0.99)["why"])
    check("and it says it is the less certain of the two kinds of card",
          not room.guess_kind(2.543, 3.8, 0.99)["sure"]
          and room.guess_kind(2.5, 3.5, 0.99)["sure"])

    print("\na small chit is a counter whatever its corners are doing")
    # ⭐️ THERE WERE TWO RULES HERE ONCE — "counter" for a small square and
    # "token" for a small disc. The designer, shown the result: "not sure I know the
    # difference between a token and a counter tbh!" There is not a firm one,
    # and a rule that asks somebody to make a distinction they cannot make has
    # failed at the only job this file has, which is taking a decision OUT of
    # naming. The shape is still said in the reason, and still visible in the
    # piece; only the question went away.
    check("a three-quarter-inch square is a counter", kind_of(0.75, 0.75, 0.99) == "counter")
    check("and so is the disc beside it", kind_of(0.75, 0.75, 0.785) == "counter")
    check("and so is a hexagon", kind_of(1.1, 1.1, 0.75) == "counter")
    check("but the reason says which of them you are looking at",
          "corners off" in room.guess_kind(0.75, 0.75, 0.785)["why"]
          and "square" in room.guess_kind(0.75, 0.75, 0.99)["why"],
          room.guess_kind(0.75, 0.75, 0.785)["why"])
    check("with no shape to go on at all, it still calls a small chit a counter",
          room.guess_kind(0.75, 0.75, None)["kind"] == "counter")
    # ⚠️ but a small thing of no describable shape at all is still nothing
    check("a small ragged scrap is not a counter", kind_of(0.75, 0.75, 0.35) is None)

    print("\n⭐️ and the shapes it must say NOTHING about")
    check("a page-sized piece — board, chart, player mat, who knows",
          kind_of(8.5, 11.0) is None)
    check("a six by nine — the same problem, smaller", kind_of(6.0, 9.0) is None)
    check("a splinter far too small to be anything", kind_of(0.2, 0.2) is None)
    check("a big disc is not a counter — it may be a template or a compass",
          kind_of(3.0, 3.0, 0.785) is None)
    # ⭐️ THERE WAS A RULE OFFERING "tile" FOR A BIGGER SQUARE, AND THESE FOUR
    # STAND GUARD OVER ITS GRAVE. Tried against a real game of 79 cut pieces it
    # spoke exactly once, and the thing it called a tile was a turn TEMPLATE.
    # ⚠️ They are worded to fence the SIZE BAND itself, because the first draft
    # of them did not and was useless: every other silence in this section
    # happens to be settled by the piece not being square, so widening the tile
    # rule to swallow whole boards left the lot of them green.
    check("a two-inch square is not called a tile — it may be a template",
          kind_of(2.0, 2.0) is None)
    check("nor is a big square — it could be half a board", kind_of(8.0, 8.0) is None)
    check("nor a whole square page", kind_of(11.0, 11.0) is None)
    check("nor is a 2in square with its corners off", kind_of(2.58, 2.57, 0.712) is None)
    # the fences round both card rules — near a card size is not a card size,
    # and neither is anything of card-ish size with the wrong proportions
    check("a squarish rectangle of card size is not offered as a card",
          kind_of(2.9, 3.5) is None and kind_of(3.98, 4.49) is None)
    check("nor a long thin one", kind_of(2.0, 4.0) is None)
    check("nor a whole page-sized rectangle", kind_of(4.32, 6.48) is None)
    check("nor a round thing of exactly card proportions",
          kind_of(2.543, 3.8, 0.78) is None)
    check("a piece with no measurements at all",
          room.guess_kind(None, None) is None and room.guess_kind(0, 0) is None)

    print("\nnothing it offers is off the room's own list")
    kinds = set()
    for w in [x / 20.0 for x in range(2, 240)]:
        for h in [x / 20.0 for x in range(2, 240, 3)]:
            for cover in (0.75, 0.785, 0.95, 0.99):
                got = room.guess_kind(w, h, cover)
                if got:
                    kinds.add(got["kind"])
    check("every kind it can ever propose is one the Kind box offers",
          kinds <= set(room.KINDS), sorted(kinds))
    check("and every guess carries the measurement it was made from",
          all(room.guess_kind(w, h, 0.99) is None
              or "in" in room.guess_kind(w, h, 0.99)["why"]
              for w in (0.5, 2.5, 8.0, 2.0) for h in (0.5, 3.5, 0.6, 2.0)))

    wrong = [d for d in done if not d]
    print("\n%s" % (("%d of %d checks are WRONG" % (len(wrong), len(done)))
                    if wrong else "all %d checks came out right" % len(done)))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
