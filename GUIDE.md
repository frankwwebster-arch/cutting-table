# The Cutting Room — how to use it

You have a board game, or the scans of one. You want each counter, card, tile
and template as its own picture, cut out cleanly, the right size, with a list
saying what each one is.

That is what this does. At the end you have **an ordinary folder**: one picture
per piece on a transparent background, named by what the piece is, at its true
printed size, with a spreadsheet beside it. Nothing in that folder is shaped
for any particular program — it is as much use to somebody making a Tabletop
Simulator mod as to somebody reprinting one lost counter at the right size.

There is one thing the room cannot do for you, and it is the slow part:
**drawing round each piece**. Everything else it does in one press.

---

## ⚠️ Read this part first

**What you cut is somebody else's work.** Copyright in a game's artwork, its
design and its words belongs to its publisher and to the artists who made it.
Scanning it, cutting it up and giving the pieces tidy names changes none of
that. **Nothing that comes out of this room is yours to give away.**

It is for your own use, with a copy of the game that you own — replacing a
piece you have lost, playing a game you already have, keeping a record of
what is on your own shelf.

> Do **not** put the pieces on the internet.
> Do **not** share them, sell them, or build them into anything you release.
> Do **not** upload them to a mod workshop, a file host or a forum.

The Cutting Room is a tool, like a scalpel is a tool. It gives you no rights
over anything you cut with it, and its authors are not lawyers: what counts as
personal or fair use differs from one country to the next, and where you stand
is yours to know. The same notice goes into every folder you export, so it
travels with the pieces.

---

## Opening it, and closing it

Double-click **Cutting Room.command** on the Desktop. A window of writing
appears — ignore it — and the room opens in your browser.

If there is no such file yet, open Terminal once and run:

```sh
python3 cutting_room.py --install-launcher
```

That puts the launcher on your Desktop, pointed at wherever this copy lives.
After that you never need Terminal again.

**To close it**, press **Close the Cutting Room** at the end of the top bar of
any page. It checks first that nothing is half-written — an import running, a
cut running, or a cutting table open in another tab with an edit not yet
saved — and tells you what it is waiting for. The page it leaves behind says
the room is closed and how to open it again.

⚠️ Do not just close the browser tab and walk away while something is still
being written. That is what the button is for.

---

## The six steps

They run left to right across the top of every page, and each one lights up as
you get to it.

![The front page](docs/guide/1-the-front-page.png)

---

### 1 · Get the scans in

**Start a game** on the front page, give it a name, and say where it lives.

Then get the pictures in. You can:

- **drop a PDF anywhere on the window** — every page becomes a sheet;
- **drop a whole folder of scans** on it;
- **drop single pictures** on it;
- or paste a web address.

Scan at **300 dots per inch** if you have the choice. The room works out every
piece's true printed size from that number, so a wrong one makes every
measurement wrong. You can correct it later, per game.

Sheets arrive named after the file they came from, and the room groups them by
what comes before the number — so `plague-01` … `plague-30` are one box, and
`core-01` … `core-40` another. That grouping is used everywhere, because a game
is worked through **a box at a time**, not a sheet at a time.

![The sheets](docs/guide/2-the-sheets.png)

The chips above the list — *All*, *To outline*, *Cut*, *Finished with* — narrow
it. It opens on **To outline**, which is the work still to do, and it remembers
which one you chose for each game.

---

### 2 · Draw round each piece

This is the slow part and the only part that is really yours to do.

Press **Outline** on a sheet and the cutting table opens: the sheet, big, with
tools down the left.

![The cutting table](docs/guide/3-the-table.png)

- **Rectangle** and **Ellipse** — drag a box or an oval round a piece.
- **Outline** — click round an awkward shape point by point, then close it.
- **Adjust** — drag any point of a shape you have already drawn; drag a line
  between two points to add one.
- **Array** — for a block of counters printed on a regular grid: draw one, say
  how many across and down, and it repeats.
- **Suggest** — the room's own attempt, from the colours. Worth pressing on a
  sheet of counters; it will not manage an island with a lagoon in it.

Your work is saved **to the game's folder, a moment after every change**. There
is no Save button and there does not need to be one.

⚠️ **The letter keys are tools**, so pressing R gets you the rectangle. That
stops the moment you click into a box that expects typing, so naming a piece
does not go rummaging through the toolbox on the way past.

⭐️ **Keep the shape** puts an outline you have drawn on a shelf, and you can
lay it down again on any other sheet — in this game or any other. A door drawn
once for one dungeon game is the same door in the next.

---

### 3 · Cut

**Cut this sheet** on the sheet, or **Cut everything** for the lot.

Each piece comes out as its own picture: full resolution, transparent
background, the edge smoothed and bitten very slightly *inside* the printed
line so the die-cut line does not show, and measured in inches.

That is the whole of this step. It takes a second or two a sheet.

⭐️ **You can cut a sheet again as often as you like.** If you fix an outline
and cut again, the names you have already given the pieces **follow them** —
even when adding one outline near the top renumbers everything below it.

---

### 4 · Say what each piece is

A picture of a counter is no use later if nothing says which counter it is. And
this, not the cutting, is where the evening goes: what a piece is *called*
comes from a rulebook or a list, not from the piece.

![The pieces](docs/guide/4-the-pieces.png)

The **Pieces** tab shows every piece at its true printed size on a one-inch
grid, with a box for its name and one for what sort of thing it is.

Things that make it quicker:

- ⭐️ **Choose several at once.** Tick the box above the list and every row
  gets a tick box, with *all shown* and *none* beside it. Tick a whole deck,
  choose the component once, and **Apply to the ticked pieces** gives them all
  the same one. A name you typed yourself is never overwritten.
- ⭐️ **The room offers a kind** — *"looks like a counter, 0.63 × 0.63in"* —
  worked out from the piece's printed size, and one press takes a whole run of
  them. Where a measurement does not settle it, it says nothing at all, which
  is the right answer more often than any particular kind is.
- ⭐️ **⏎ in the name box** saves and moves to the next piece. The arrow keys
  move between pieces too.
- ⭐️ **Match** is the fastest way if you have typed the box's contents list:
  a board of every piece beside the list of components, and you drag a name
  onto the piece it is.

![Match](docs/guide/5-match.png)

**Other things a piece can carry**, all optional:

- **Its back** — a card's back is *another piece*. Cut the back once and point
  every card in the deck at it. ⭐️ Set that back piece's **Kind** to *card
  back* and the list stops offering you all two hundred pieces.
- **How many the game needs** — for one design used over and over, like the
  one card that appears twenty times in a deck. You still cut it **once**.
- **Turn it** — quarter turns, applied everywhere the piece is shown. The
  picture on disk is never rewritten, so you can change your mind for ever.

---

### 5 · Check what you have against the box

Optional — cutting works perfectly well without it — but it is how you know
when you are finished.

![The checklist](docs/guide/6-the-checklist.png)

Press **Paste the contents list** and type in the box's own contents list, one
component to a line:

```
26 Damage counters
Turning template x2
Long range ruler
9 | Large templates | template
```

Against each component the room then says **cut**, **probably cut** (a name
matches, but nothing is joined up — press *Confirm the likely links*) or **not
yet**, and gives you a percentage.

⭐️⭐️ **One line, one piece — unless every one is different.** A sheet prints
twenty-six identical damage counters and the game repeats one for ever, so *26
Damage counters* wants **one** piece cut. But *24 Damage cards* is twenty-four
different pieces of card. Nothing in a printed contents list tells those apart,
so each line has an **all different** tick and only you can set it. Until you
do, a deck of thirty-two counts as done the moment you cut one card of it.

---

### 6 · Check the cut, then take it away

On **Take it away**, above the button, is the last thing to read before the
pieces leave: **the cut checked against the contents list**. It changes
nothing; it just tells you what it sees.

![Take it away](docs/guide/7-take-it-away.png)

**Read the whole check** opens it as a page you can print and work through with
the box open in front of you.

![The check](docs/guide/8-the-check.png)

It says, set by set:

- **components with nothing cut** — the plain gaps;
- **not enough cut yet** — *Damage cards, 24 of 32*;
- **counted only because a name looks right** — a guess, and it says so;
- ⭐️⭐️ **decks the list counts as a single card** — read this one first, or
  the percentage above it is flattering you;
- ⭐️ **cut pieces that answer to nothing on the list** — the one nothing else
  can tell you. Each is either something the printed list forgot, a piece cut
  twice, or a piece cut from the wrong place;
- **pieces with no name**, **held back**, and **set aside**.

Then press **Write the folder**. You get:

| | |
|---|---|
| `pieces/` | one picture per piece, transparent background, named by what it is |
| `inventory.csv` | the same list as a spreadsheet — opens in Numbers or Excel |
| `inventory.json` | the same list again, for a program to read |
| `contact-sheet.html` | every piece at true printed size on one page, to print |
| `still-to-cut.html` | the checklist, to print and take to the table |
| `check-against-the-list.html` | the check above, to read and print |
| `laser/` | cut files for a laser or craft cutter, true size in millimetres |
| `README.txt`, `COPYRIGHT.txt` | what is in the folder, and the notice above |

⚠️ The folder is **replaced whole** every time, so keep nothing of your own in
it. Everything in it can be made again from the sheets and the outlines.

---

## Nothing is ever thrown away

Two things are worth knowing before you press anything that sounds final.

⭐️ **Setting a piece aside does not delete it.** There are two identical ice
fields on the sheet and the game only needs one — so the second is *moved* to a
spare folder, keeps its name, stays in the list dimmed and marked, and comes
back in one press. The hand-over does not look inside that folder, so it simply
is not handed over. Deleting a whole sheet is the only thing in the room that
really deletes, and it says so plainly first.

⭐️ **The room keeps its own history.** Three things in a game cannot be rebuilt
from the scans: the **outlines** you drew, the **names** you gave the pieces,
and the **checklist**. Every time one of those is written, the room keeps the
copy it replaced — the last sixty of each. **Settings** lists them, says what
was in each, and puts one back; the copy it replaces is kept too, so restoring
is not a one-way door either. You do not have to remember to do anything.

---

## When something looks wrong

**A button says "no such call".** The room is running older code than the page
in front of you — this happens when the room has been open while it was
updated. Close it and open it again. A banner across the top says so when the
room notices it itself.

**Something you just did does not show.** Everything saves a moment after you
change it. If a count looks stale, move to another tab and back.

**You lost something.** Look in **Settings → if something goes wrong**. The
outlines, the names and the checklist all keep their last sixty copies.

**You do not know what a button does.** Point at it — every button, link and
box in the room carries a plain sentence saying what will happen. Or press
**What does this do?** at the top, and the room writes them all out under the
controls at once.

---

## Where to read more

- **[ROOM.md](ROOM.md)** is the full reference — every screen, every button,
  every corner of the room. This guide is the walk-through; that is the manual,
  and where the two ever disagree, believe ROOM.md.
- **[README.md](README.md)** is the short public description of the tool.
- **[BACKLOG.md](BACKLOG.md)** is what is built, what is next and what is known
  to be missing.

---

*The pictures in this guide are of a **demonstration sheet** drawn by the tool
itself out of nothing — no game's artwork appears anywhere in this repository.
Re-make them with `docs/make_guide_pictures.sh`.*
