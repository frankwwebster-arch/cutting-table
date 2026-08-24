# Backlog — the Cutting Room

The live list. `CLAUDE.md` is how the thing works and why — **and the house
rules for working on it, which is where to start**; `ROOM.md` is how to use it.
This is what happens next.

⭐️ **Take one thing from *NOW*, say which and why, and see it through** — code,
documents, checks, commit, push. Run `check/check.sh` before you begin as well
as when you finish. The full version of all of that is in CLAUDE.md under
*Picking the work up*.

**Legend:** `[ ]` not started · `[~]` part done · `[x]` done · ⭐️ next up

---

## NOW

### `[x]` ⚠️⚠️ Setting a piece aside is written down, always — **fixed**

The designer, 24 August 2026: *"setting pieces aside seems pretty temperamental — I
just tried to get rid of multiple copies of [one piece], but didn't seem to
work, either in bulk when suggested, or individually when selected in
#pieces."*

It half worked every time, which is worse. The file moved; the **mark** was
written only onto pieces the manifest already knew — and an unwanted duplicate
is exactly the piece nobody has named — so the room went on drawing it as
though it were in play, and a re-cut would have handed it back to the game.
Reading the designer's own project found three pieces in that state.

- `[x]` The mark lands on every piece set aside, named or not.
- `[x]` ⭐️ **The folder is the truth**: anything in `pieces/spare/` is set
  aside whether or not it was written down, so pieces already adrift repair
  themselves when the list is next read — and before a re-cut, which is when
  the folder stops being able to say so.
- `[x]` The press says what actually happened, instead of always saying it
  worked.
- `[x]` ⭐️ **Several at once** from the *choose several* bar, which is what
  "get rid of multiple copies" actually asks for. The same button brings them
  back.

See CLAUDE.md 58. Seven new checks, 327 to 334; teeth tried.

### `[x]` ⭐️⭐️ A deck that is full says so, even when it is thirteen pictures — **fixed**

The designer, 24 August 2026: *"I need to finalise a deck. It contains 13 different
cards, one of which has 20 copies — thus 32 cards in total. I have marked the
20x component, but [the deck] reads — relatively justifiably — 13 of 32. How
do I fix given the deck is technically complete?"*

Both halves were already there and were not speaking: **all different** says
the line's thirty-two cards are not one design printed thirty-two times, and
**How many the game needs** on the piece says the game wants that one design
twenty times. The checklist counted pictures where the quantity means cards.
A cut piece now fills as many of the wanted quantity as the game wants of it,
so the deck reads **32 of 32 ✓** with *3 pieces, repeated to fill it*
underneath — because the number has to say what it is made of.

⚠️ Nothing guesses it, and taking the mark off puts the deck straight back to
part-cut; a check tries exactly that. See CLAUDE.md 56.

### `[x]` ⚠️ The bulk bar's list of card backs went stale — **fixed**

The designer, 24 August 2026: *"I have marked 6 different elements as card backs. When
I do 'choose several at once' only one of those backs appears in the backs
dropdown. It should contain the other card backs so I can batch add it (or I
have to go through every card manually)."* The list was rebuilt only when the
narrowing switched on or off, so it was built when the first back was marked
and never again. It is rebuilt from what it is made of now, and so is the
component list beside it, which had the same fault waiting for a component
added while the bar was open. See CLAUDE.md 57.

### `[x]` ⭐️ A user guide, written properly — **built**

`GUIDE.md`, with eight pictures. Organised by the **job** and not by the
feature: get the scans in · draw round each piece · cut · say what each piece
is · check it against the box · take it away — the same six steps the room is
built round, so the guide and the room agree.

⭐️ **ROOM.md is the source and wins where they disagree**, and the guide says
so in as many words: the guide is the walk-through, ROOM.md is the reference.
That is the only thing keeping them from drifting apart (fault 24).

⭐️ **The pictures are made, not taken.** `docs/make_guide_pictures.sh` builds a
throwaway game out of the demonstration sheet, in a home of its own on a port
of its own, cuts and names some of it, and photographs every screen. Run it
again whenever a screen changes — a guide illustrated with last month's
screens is worse than one with no pictures. ⚠️ Nothing in those pictures is
anybody's artwork, which is why they may sit in a public repository.

What is left of it:

- `[ ]` **An Artifact of it**, for reading on a phone or handing to somebody.
  ⚠️ Generated FROM `GUIDE.md`, never written twice.
- `[ ]` **Arrows on the pictures.** The designer's original point was *"one screenshot
  with an arrow on it"*; they are honest screenshots with no arrows yet.

### `[x]` ⭐️⭐️ Check the cut against the contents list, at the end — **built**

The designer, 24 August 2026: *"I want (once I've done my cutting work) to be able to
run a verification check against the original component index - a secondary
check to ensure we have every piece cut. Is that possible?"* It is, and it is
on **Take it away**, above the button, and in the exported folder twice — see
*Done*, below, and ROOM.md for what it says.

What is left of it, none of it urgent:

- `[ ]` **A way in from the report to the piece.** Every line about a piece
  names its stem; clicking it should open that piece. `?tab=pieces&piece=<stem>`
  would do it, and it is the same door a game engine would want (see the item
  below).
- `[ ]` **Fold the report by set**, once a game has more sets than fit a
  screen. The game it was built on has four and it is fine.
- `[ ]` ⭐️ **Say what a piece measures beside the orphans.** A piece that
  answers to nothing on the list is often recognisable from its size alone,
  and the measurements are already cached.

### `[ ]` ⭐️ The other end of the check — the game ingesting the pieces

The designer, 24 August 2026: *"there's validation which can be fed back by the game
engine into which I drop all the components. Surely any game I build will
have to have its own library of pieces, and will need to know in
advance what those pieces will be, having digested the rulebook. So not only
should there be a secondary [check], but there should be a smart input process
into a game, so that all the pieces can be practically catalogued by the game
engine as it ingests them — which can include user verifying each one (and
thereby learning of any missing or wrongly attributed — and then go back to the
cutting-table to make fixes)."*

⚠️⚠️ **Most of that is the GAME's, not the room's** — see the top of
`CLAUDE.md`. A library derived from a rulebook, and a screen for walking
through it saying yes or no, are shaped like one particular game, and every
such thing belongs in that game's own repository. The room's job ends at the
folder of named, measured pictures with an inventory beside it, and that is
what the great majority of its users want.

⭐️ **What is the room's, and is worth doing here:**

- `[x]` The **end-of-job report** above — **built**, and it is written as
  JSON beside the printable page for exactly this reason: the engine gets the
  room's own account of what is missing without re-deriving it.
- ⭐️⭐️ **And the game already holds the answers.** The designer, 24 August 2026:
  *"if you talk to the game project, I think you'll see that it's
  been able - in advance of me formally handing anything over - to determine
  the value/wording/rules attached to cards still in cutting-table."* Quite
  so: `data/cards/*.json` there holds 225 cards across twelve decks, each with
  its name, its casting value and its printed effect, transcribed before a
  single card was cut. So the traffic runs BOTH ways, and the room's side of
  it already exists: `PUT /api/p/<id>/wanted` takes a whole contents list, so
  **the game can write the room's checklist** rather than anybody typing it
  twice — with `each` and `qty` right, which is what makes the counts mean
  anything. ⚠️ That script is the GAME's: it knows what a card deck is.
- ⭐️ **The way back in.** `cut_from` in `inventory.csv`/`inventory.json`
  already carries the piece's stem, which is the one name the room and the
  game can both say. That is what makes *"this one is wrong, go and fix it"*
  possible at all, so **it must not be dropped**, and it should be easy to
  open the room straight at a piece — `?tab=pieces&piece=<stem>` — so the
  engine can link to it.
- ⭐️ **Pieces that answer to nothing on the list** — the inverse in the
  report, and precisely their *"wrongly attributed"*.

Nothing here should know what a rulebook is.

### `[~]` Opening and quitting without a terminal

The designer, 22 August 2026: *"a simpler way to open and quit. I don't like terminal
at the best of times."*

- `[x]` ⭐️ **Quit from the room itself.** *Close the Cutting Room* sits at the
  end of the top bar on every page. It asks the room what is still in flight
  first — an import or a cut running, or a cutting table open in another tab
  with an edit not yet written down — names each one in plain English, and only
  then closes. The page it leaves behind is a sign on the door saying the room
  is closed and how to open it again. ⚠️ The room cannot see a browser tab, so
  every open table says hello every eight seconds; see CLAUDE.md 21.
- `[x]` **A launcher in the repository.** `python3 cutting_room.py
  --install-launcher` writes `Cutting Room.command` to the Desktop, carrying
  whatever path this copy was cloned to and naming the python it was run with
  (`/usr/bin/python3` where that will do, because a command-line-tools path
  moves when Xcode is updated). An existing launcher is kept as `.was` rather
  than overwritten. The designer's own hard-coded one is no longer special.
- `[ ]` **No terminal window at all.** A minimal `.app` bundle — a folder with
  an `Info.plist` and a shell script in `MacOS/` — launches with no visible
  terminal and can carry an icon. This is all that is left of the complaint:
  quitting no longer needs the window, but opening still shows one.

⚠️ Whatever is built must still work when the room is started the old way, and
must not need anything installed.

### `[x]` Shapes kept — draw a shape once, use it in any game

**Built, 23 August 2026**, asked for by name, and grown twice the same day as
the designer thought about it — a shape can be scaled, and a shape can tell a sheet
its scale. See *Done*, below. What is left of it, none of it urgent:

- `[ ]` **Renaming a kept shape.** Today a name is given when the shape is
  kept and the only way to change it is to forget it and keep it again from a
  piece that has its shape. Two presses, but a typo is annoying.
- `[ ]` **Ordering the shelf** — most used, or most recently used, rather
  than newest first. Worth nothing until somebody has thirty shapes.
- `[ ]` **Lay a shape turned.** It lands the way up it was kept, and a quarter
  turn is a drag on the transform box afterwards. Fine for a door; tedious for
  a corridor that runs both ways.
- `[ ]` ⭐️ **The scale carried from sheet to sheet.** *Scale the sheet to this
  shape* fixes one sheet at a time, and an expansion is thirty sheets from the
  same scanner at the same setting. Offering the last scale to the next sheet
  of the same run would turn thirty measurements into one. ⚠️ It must stay an
  offer — a scan halfway through a book can change.

### `[x]` ⭐️ Every control says what it does

**Built, 23 August 2026.** The designer: *"a very useful tool (and in fact perhaps a
habit to get into) is adding helpful instructional text to my platforms like
Cutting Room. I don't, for example, have any idea what 'straight to the table'
means on the project selection screen… And that's not just for me,
obviously!"* See *Done*, below. It is now a **house rule** in CLAUDE.md and a
check, which is the part that matters: the buttons that existed were easy to
fix, and the next one is the one to stop. What is left:

- `[ ]` **The room's own prose, read again by somebody new.** The tips explain
  the controls; some of the surrounding text still assumes you know what a
  mask or an outline is.
- `[ ]` **A first-run walk through the six steps**, rather than the welcome
  panel that only appears on an empty room.

### ⭐️ A light ground, and displays generally

The designer, 22 August 2026: *"I'd like to consider some different displays (eg white
background rather than the black)."* **Next up.**

⚠️ **Read the reason for the dark ground before changing it.** The editor's own
stylesheet says it: *"A workbench that commits to one look on purpose: the
printed sheet is the only thing on the page whose colour must be judged, so
everything round it is a quiet dark ground in both host themes."* A scanned
counter is being looked at against that ground while it is outlined, and a
white surround changes how its colour and its edges read. That is an argument
for care, **not** an argument for refusing — their eye is the instrument, and if
a light ground suits them better it wins. Worth separating:

- **The room's own pages** (home, project, checklist, match) — mostly text and
  thumbnails. A light ground here is uncontroversial and is the easy half.
- **The Cutting Table itself** — where the sheet is judged. If this goes light,
  offer it as a *choice* rather than a swap, and look at a real counter sheet on
  both before deciding.
- **The baked offline page** shares the template, so whatever is done must work
  with no server behind it.

There is no theme mechanism at all today: `room/room.css` and the template's
`:root` block each hard-code one palette.

### ⭐️ The designer is using it, and feedback comes back in new chats

Two games are loaded and they are cutting. **What they say next outranks
everything on this list.** Still worth their eye:

1. **The outlining itself**, which is where the hours go. *Add the suggested
   outlines* on a counter sheet either saves the whole evening or wastes it,
   and nobody has watched them use it on a fresh set.
2. **Whether the checklist is worth keeping.** 209 components was compiled for
   one game by reading three printed contents lists. Whether that is a
   pleasure or a chore for the next game is not yet known.

### `[~]` Cut a real game's counters — the set that proves the loop

Core sheets 1, 2, 4 and 6. They are the easiest kind (rectangles and circles on
a plain ground, so the flood finds them) and the most valuable, because the
game draws stand-ins for every counter it has not been given. **One of each
design** — the game repeats it for ever.

- `[x]` **Sheet 1 is cut**, 22 August 2026, and came through clean: *"all
  checks out well… generally excellent."*
- `[ ]` Sheets 2, 4 and 6.

⭐️ **The fiddly part is naming, and it is not a tool problem.** The designer: *"naming
is always going to be the fiddly bit here as it will tend to rely on 3rd party
lists etc, or rules manuals which may be tricky to comprehend."* The room can
cut a sheet in a press; **what a piece is called comes from outside** — a
contents list, a rules manual, somebody's forum post. That is the real cost of
a new game, and it is what the two ideas below are aimed at:

- `[x]` **Guess the kind** from size and shape — built, 22 August 2026. See
  *Done*, below.
- ⭐️ **Learn the checklist from what is cut** — its own entry below; it is now
  the best of the three.
- **A shared folder of checklists**, since a game's contents list is public
  knowledge and only has to be typed once by anybody.

### `[ ]` ⭐️ Learn the checklist from what is cut

The inverse of Match, for a game with **no contents list at all** — which is
most games, and certainly any game whose list nobody has bothered to type out.
Rather than reading a component list in and ticking pieces off against it,
**group the cut pieces by look-alike and printed size, show each group, and let
the person name the group once.** Twenty identical damage counters become one
line of the checklist in one typing.

Everything it needs is already built and already on the screen somewhere else:
the 144-bit look-alike hash and mean colour that the review uses to cluster,
the printed measurements, and now the **kind the room offers from those
measurements** — so a group can arrive pre-labelled *counter* and only want its
name. The work is the interface, not the arithmetic.

⭐️ **Why this one is worth more than anything that speeds up cutting:** naming
is the expensive part, and it is expensive because it comes from outside the
room. This is the only idea on the list that makes a checklist appear without
anybody having to find a rules manual first.

⚠️ It must not become an automatic checklist. The room may propose the groups;
what a group is *called* is a judgement and stays the person's, exactly as with
the kinds and the look-alikes.

### `[ ]` A demo project, so a stranger can try it with nothing

`demo/make_demo_sheet.py` already draws a pretend sheet — deliberately awkward
in the one way that matters, with the same colour inside a piece as outside it.
**Wire a "Try it with a demo sheet" button into the first-run welcome** that
makes a project, imports the demo, and lands on the table. Today somebody who
finds this repository has to own a board game before they can see what it does.

---

## Known gaps

### `[ ]` ⚠️ It is macOS-only in two places, and needlessly

- `doc_to_docx()` shells out to **`textutil`**, which exists only on a Mac. On
  anything else an old binary `.doc` should say so plainly rather than fail
  with a confusing error. LibreOffice (`soffice --convert-to docx`) is the
  obvious fallback where it is installed.
- *Open the folder* uses `open`, guarded by `sys.platform == "darwin"`, so it
  quietly does nothing elsewhere. `xdg-open` and `explorer` are one line each.

Everything else — the server, the cutting, the editor — is portable already.

### `[x]` The way out — **built**, and it is generic

See *Done*, below. `export/` is a plain folder: pieces named by what they are,
an inventory as CSV and JSON, a contact sheet, the printable checklist, and
laser cut files. Still wanted, but not urgent:

- `[ ]` **A ZIP of it**, for handing to somebody in one file.
- `[ ]` **Print-and-play out** — the pieces nested back onto A4 with crop
  marks, rather than cut in the sheet's own positions. Needs a matching print
  file to be worth anything, which is why the first version does not nest.
- `[ ]` **Export one kind, or one sheet**, rather than all of it.

### `[~]` A test suite — the editor is covered, the cutting is not

`check/check.sh`, 334 checks in about a minute. It makes a throwaway 66-sheet
game out of the demonstration sheet, in a registry of its own, and drives a
real Chrome over it.

Covered: ⭐️ **a deck counted against its quantity while a counter still
needs only one**, whose teeth were tried · ⭐️ **one line of a contents list split into the components it
really stands for**, and the names that must and must not follow it · ⭐️ **every button on every page saying what it does**, and the
explanation really appearing when you point at one · ⭐️ **a shape kept and laid down again**, in inches, across sheets
and across games, with the favouriting and the search · **a shape laid at
another size without being squashed** · ⭐️ **a shape telling a sheet what its
scale really is**, whose teeth were tried · **a shape taken off a piece already
cut** · ⭐️ **the kind the room offers from a piece's size — and, more to the
point, the shapes it refuses to speak about** · every script parses · **the editor the room SERVES parses, not just
the template** · the editor patches still match · the page does not stretch
itself · one sheet's picture fetched, not sixty-six · a rectangle drawn with
the pointer · **typing a name does not work the tools** · **the outline and its
name reach the project's `outlines.json` on disk** · leaving a sheet and coming
back · **the cut itself**, with the piece read back off the disk at its printed
size in inches · ⭐️ **names, and variant marks, following their pieces across a
re-cut**, including the removals that used to leave a name behind · a name
dropped on a piece raising no complaint · a turned piece turning its picture
everywhere without being clipped · the offline baked page.

Still wanted:

1. **Import**: a PDF, a .docx, a ZIP, a folder — each to its sheet count.
2. The **look-alike hash**, which has been wrong once already (8×8 grey called
   NO MOVEMENT and NO FIRING the same counter). Worth knowing: a bright flag
   in one corner is enough to push two otherwise identical cards past the
   threshold, which is how the fixture for the variants work was built.

### `[ ]` The suggestion cache is not invalidated by a new mask

`cache/<sheet>.suggest.json` is written once. If a `-starter.png` mask appears
in `masks/` afterwards, the old flood-based suggestions are still served.
Delete the cache file when the masks folder changes.

### `[ ]` Sheets cannot be re-ordered, re-prefixed or merged

A sheet's id is `<prefix>-<page>` and is the key its outlines are filed under,
so renaming one would strand them. That is the right constraint, but there is
no way at all to fix a bad prefix chosen at import — you delete and re-import,
losing the outlines. A rename that moves the outlines with it is a small job.

### `[ ]` Google Drive is a dead end and should perhaps say so louder

Pasting a link works only for a file shared "anyone with the link"; a folder
cannot be fetched at all. **Dragging the downloaded folder is better in every
case**, and the interface now says so. A real Drive integration would need
OAuth, a client secret and a consent screen — a great deal of machinery for
something a drag already does.

### `[ ]` Touch and small screens

Untested and almost certainly poor. The editor is a mouse tool — outlining on a
tablet is a genuine design question, not a port.

---

## Ideas worth thinking about, not yet decisions

⭐️ The first three below stopped being speculation on 22 August 2026: The designer cut
a real sheet 1 cleanly and named it by hand, and reported that **naming is
the fiddly part, because it comes from outside the room** — third-party lists
and rules manuals. Anything that takes a step out of naming is worth more than
anything that speeds up cutting.

- ~~**Guess the kind.**~~ Built — see *Done*. What it left behind is worth
  knowing: it says nothing about a piece the size of a page, or a two-inch
  square, because a measurement genuinely cannot settle those. **Only a
  picture can** — which is an argument for the *second pair of eyes* idea
  below rather than for a cleverer measurement.
- ~~**Learn the checklist from what is cut.**~~ Promoted out of the ideas and
  into *NOW*, above — it is the best of the naming ideas left.
- **A second pair of eyes on a sheet**: after a cut, show the sheet with the
  pieces knocked out and ask "is anything still printed here?" That is exactly
  what the marked-up thumbnail shows; it could be a step rather than a picture.
- **Print-and-play out**, not just in: lay the cut pieces back onto A4 with
  crop marks. The cutter already writes an SVG at true size for a laser.
- **More games than one person's shelf.** The checklist format is plain JSON
  and a game's contents list is public knowledge. A folder of them, shared,
  would make the tool immediately useful to somebody who owns the scans and
  not the patience.

---

## Done

### 24 August 2026 — nothing here names a game, a publisher or a person

- `[x]` ⚠️⚠️ **The last of one game's own names out of the tool**, after an
  earlier pass had taken out the publisher and the products but left the
  components: player markers, movement templates, terrain tiles, damage
  counters and a range ruler now stand where a particular box's pieces did.
  The measurement was always the evidence; the name never was.
- `[x]` ⚠️ **And the owner's name, and the pronouns with it.** they/them
  throughout — nobody's are written down here, and a document with no name in
  it should not still say *he*. The licence holder is *the Cutting Room
  authors*; ⚠️ the repository's own web address still carries the account name
  it is hosted under, and only the account holder can change that.
- `[x]` ⭐️⭐️ **A check that fails if any of them come back** — 27 words,
  searched with the line breaks taken out, because that is exactly how the
  last one hid through two passes that were looking straight at it. ⚠️ Its
  first run reported the repository riddled with all 27: it had found its own
  word list. See CLAUDE.md 55.
- `[x]` **`AGENTS.md` is a signpost now, not a second copy.** It was the same
  working document written for another assistant and had drifted **213 lines**
  from `CLAUDE.md` in three days — one said fifteen pieces of work where the
  other said twenty-one, and it was missing the last five faults. That is the
  fault this codebase warns about most, arriving in the documents themselves.
- `[x]` **1 new check** — 321 to 322.
- `[x]` **7 new checks** — 327 to 334: setting aside a piece nothing has ever
  named, in bulk and singly, the file really being in the spare folder, the
  piece staying on the list dimmed, the same button bringing it back, and a
  piece put in `spare/` by hand being taken as set aside. ⭐️ Teeth tried: the
  fault put back turns four of them red.
- `[x]` **5 new checks** — 322 to 327: a deck filled by a design the game wants
  twenty-two times, the mark taken off again, and the bulk bar's list of card
  backs taking in a back marked while it is open. ⭐️ Teeth tried: both faults
  put back turn exactly those checks red and nothing else.

### 24 August 2026 — the cut checked against the contents list

- `[x]` ⭐️⭐️ **The check the designer asked for by name**, on *Take it away* above
  the button and in the exported folder twice — `check-against-the-list.html`
  to read and print, `.json` for whatever ingests the pieces. Per set: nothing
  cut, not enough cut yet, counted only by a guess. Then the pieces that
  **answer to nothing on the list**, the ones with no name, the ones held back
  and the ones set aside. ⚠️ It reports and never fixes.
- `[x]` ⭐️⭐️ **Decks the list counts as a single card** — the finding that
  came out of reading the real game rather than out of any reasoning. **Nine
  of one game's twelve decks** had never been set to *all different*, so
  each wanted one piece: a deck of thirty-two would have read as done on the
  first card cut, and the percentage above it meant nothing. ⚠️ And it speaks
  only about a **deck** — written to include cards as well it went from nine
  findings to twenty, and all eleven it added were wrong. See CLAUDE.md 52.
- `[x]` ⚠️⚠️ **`check/check.sh` was reporting failure on a clean run** — and,
  worse, leaving its throwaway game in `/tmp` when it did. A failing command
  in an EXIT trap under `set -e` ends the trap and takes the exit status with
  it, and the `kill` in it fails routinely because the last section closes the
  room *from the room*. See CLAUDE.md 53.
- `[x]` **19 new checks** — 294 to 313 — including the two that matter most:
  that a counter printed twenty-six times is **not** reported as a loose deck,
  and that a game with no contents list says so rather than reporting every
  piece it has as answering to nothing.

### 24 August 2026 — a flag you can answer, and two lists that were haystacks

- `[x]` ⭐️⚠️ **Every flag on a piece can now be answered, including by saying
  it does not matter.** The designer: *"some of the pieces I've cut are flagged as
  RUNS OFF THE SHEET… I don't see a way to remove that flag (because it doesn't
  matter)."* **That is fine** on the piece stops the room flagging it for that
  reason, and **Flag it again** puts it back. The real damage was to the list:
  a flag nothing can clear means *Worth a look* never empties, so it stops
  being read at all. The answer is written on the piece, so it survives a
  re-cut. See CLAUDE.md 50.
- `[x]` ⭐️ **A card back can say it is one**, and then *Its back* offers only
  the backs — six pieces to choose from instead of two hundred and twenty-one.
  It is a `kind`, because a back IS a piece; nothing guesses it; and the
  narrowing gives up rather than showing an empty list.
- `[x]` ⭐️⭐️ **The component dropdown puts your own box first.** *"If I'm
  working with one supplement's elements, there doesn't seem to be a need to
  include all the possible choices for the core and the other boxes."* The
  room works out which set a box of sheets answers to **from the links already
  made**, so it needs nothing set up. ⚠️ It orders; it never hides. See
  CLAUDE.md 51.
- `[x]` **21 new checks** — 273 to 294 — including the mark surviving a re-cut,
  and ⚠️ one of them written to fail loudly rather than skip: the first version
  of the banding check was wrapped in an `if`, the throwaway game did not meet
  its condition, and all three checks silently did not happen while the run
  stayed green.

### 24 August 2026 — the room keeps its own history now

- `[x]` ⭐️⭐️ **The three files that cannot be rebuilt keep the copy they
  replace**, up to sixty each, automatically, in `<project>/history/`. After a
  bug of the room's own ate two components, what saved them was git — which
  the designer does not use and should not have to: *"I'm afraid this means nothing
  to me - it needs to be automated if it needs to happen."*
- `[x]` ⭐️ **And it can be reached without a terminal.** Settings lists every
  copy with what was in it, and puts one back; the copy it replaces is kept
  too. See CLAUDE.md 49.
- `[x]` ⚠️ **A save that changes nothing keeps nothing** — the room saves after
  every edit, and sixty identical copies would push the real history off the
  end.
- `[x]` **9 new checks** — 264 to 273.

### 24 August 2026 — the checklist was removing the wrong component

- `[x]` ⚠️⚠️ **A data-losing bug, found by the designer asking me to verify it.**
  *"removing a piece in the checklist doesn't work - verify that."* It removed
  **the wrong component**: a save replaces the list, the rows on screen were
  left holding dead objects, and `splice(-1, 1)` took the last component off
  instead. Every row handler works by **id** now. See CLAUDE.md 45.
- `[x]` ⭐️ **A component can be moved between sets**, and a set can be made —
  neither was possible. *"So how do i get this in the right place, which is
  within the other box?"* The **Set** column does both.
- `[x]` ⭐️ **A card's back is another piece** — cut once, pointed at by every
  card in the deck, set one at a time or over a whole deck at once. See
  CLAUDE.md 46.
- `[x]` ⭐️ **How many the game needs** — one design cut once and used twenty
  times, which the manifest had no way to say. See CLAUDE.md 47.
- `[x]` ⚠️ **The bulk bar's default no longer undoes anything.** See CLAUDE.md 48.
- `[x]` **1 new check** — 263 to 264 — plus the removal fault proved by hand
  first: the dialog named one component and a different one disappeared.

### 24 August 2026 — a fold was swallowing new components

- `[x]` ⚠️⚠️ **Fixed.** The designer: *"BUG - adding a new component does not work…
  typed in the name, clicked add, and nothing happened."* It had worked: the
  component was on disk and its row was in the table, inside a set they had
  folded away. Every way of adding a row now **opens the set it lands in** —
  adding one, pasting a list, and splitting a component into its parts.
- `[x]` **And it says where the row went**, then brings it into view and marks
  it for a moment. Nothing in a list of two hundred should have to be hunted
  for straight after being made. See CLAUDE.md 44.
- `[x]` **1 new check** — 262 to 263.

### 24 August 2026 — naming a deck at once, and starting a piece again

- `[x]` ⭐️ **Bulk apply.** The designer: *"if I can select all 32 cards in a deck, I
  should be able to apply the correct card deck label to them all in one
  go."* Tick boxes on the piece rows, *all shown* / *none*, one component,
  one press. ⚠️ Fills blanks only — a name somebody typed is never overwritten.
- `[x]` ⭐️ **Start this piece again** — every box on a piece emptied at once,
  for one filled in from the wrong row. Leaves the picture, the outline, being
  set aside and the look-alike mark alone, and says so.
- `[x]` ⭐️ **The green CUT pill shows the piece it is vouching for**, on hover,
  without leaving the checklist.
- `[x]` ⚠️ **The tick boxes went in and vanished** — appended to the row, then
  wiped by the row's own `innerHTML`. See CLAUDE.md 43.
- `[x]` **8 new checks** — 254 to 262.

### 24 August 2026 — seeing a look-alike, and one box at a time

- `[x]` ⭐️ **Pieces works in boxes, not sheet numbers.** The designer, an hour after
  the same fix landed on Match: *"the Pieces view is now pretty useless, and
  very frustrating to use. I don't want to go sheet by sheet, I'm much more
  likely to want to see core or supplement pieces - the random
  sheet numbers are not useful."* It gathers by box by default, and its Show
  list offers each box with its sheets under it.
- `[x]` ⚠️ **One `bookOf()`, used by Sheets, Pieces and Match.** The complaint
  arrived twice in a day because the first fix was made where it was reported
  rather than where it belonged. See CLAUDE.md 42.

- `[x]` ⭐️ **A look-alike can actually be looked at.** The designer: *"it's incredibly
  difficult to see them in the tiny viewport it provides - can you make them
  appear larger/preview on hover (I don't want to click away to another
  page)."* The tiles are twice the size, and hovering one shows the piece's
  **full picture** at 360px under the pointer with its id and printed size.
  The same on the row beside a suggested kind. See CLAUDE.md 40.
- `[x]` ⭐️ **Match can be held to one box.** The designer: *"otherwise I get served
  with 200+ objects from across the whole game when I'm just trying to
  rationalise one supplement."* The board could be narrowed to one sheet or not
  at all, and a supplement is thirty sheets. See CLAUDE.md 41.
- `[x]` **9 new checks** — 242 to 251. Two of them failed for reasons that
  were not the code: a hover sent with a button named on it is a drag, and the
  thumbnail was 1496 pixels down a 963-pixel window.

### 23 August 2026 — the folding was shredding the Pieces list

- `[x]` ⚠️⚠️ **Fixed.** The designer: *"on #pieces the collapse/expand mechanic is
  going awry, just not working correctly, seems to be segmenting the core box
  over and over."* A set was being taken to be "the rows that happen to sit
  together", and on Pieces they do not: a piece **file the index knows nothing
  about** has no sheet, sorts into the middle of a sheet's run by name, and
  cuts it in two. Both halves then carried the same fold id, so each claimed
  all the rows and folding one hid the other's.
- `[x]` **Gather first, render second** — one `gather()` for all three lists.
  It was latent on the Checklist and Match too, where a component added by
  hand lands at the end of the list whatever set it belongs to.
- `[x]` **A piece with no sheet had an empty heading**, which reads as a fault
  in itself. It says *Not off any sheet this project knows* now — worth
  knowing about, since a project's pieces folder can sit inside a game's own
  repository, where anything else in there shows up.
- `[x]` **5 new checks** — 237 to 242 — and their teeth were tried: put the
  adjacency grouping back and four go red. See CLAUDE.md 39.

### 23 August 2026 — a room running old code says so

- `[x]` ⚠️ **the designer hit "no such call" pressing a button built that afternoon.**
  Nothing was wrong with the button: their room had been open for hours, and a
  room serves its **pages** off the disk every time while its **Python** is
  whatever was loaded when it started. New button, old route.
- `[x]` ⭐️ **The room compares its own source against the clock it started at**
  and every page carries a plain band across the top when they disagree:
  *close the room and open it again*, and *nothing is at risk*. See CLAUDE.md
  38 — and expect it every time a session adds an endpoint while the room is
  open.
- `[x]` **5 new checks**, one of which reads a promise back as an answer and
  had to be rewritten — 232 to 237.

### 23 August 2026 — every list folds

- `[x]` ⭐️⭐️ **Sheets, Pieces, Match and the Checklist all fold.** The designer, having
  had it in Match: *"I want the same ability to collapse and expand
  core/expansions/extras etc throughout the platform (eg in Checklist, sheets,
  match, pieces etc) - it's super helpful."* Every heading has an arrow and a
  count; each list remembers its own folds, per game.
- `[x]` ⚠️ **One mechanism, not four.** Four lists that each grew their own
  would drift apart. The one trick that made it possible without rebuilding a
  grid, a table and two columns: rows are hidden **where they stand**, not
  moved into a wrapper. See CLAUDE.md 37.
- `[x]` **7 more checks** — 225 to 232, and they are as much about the four
  lists agreeing with each other as about any one of them.

### 23 August 2026 — Match folds a set away

- `[x]` ⭐️ **Each set of components folds.** The designer: *"in Match, it would be very
  helpful to be able to collapse sections eg for [the] Core Box, [one
  supplement, another]… Just needs an arrow to expand collapse. Or just some
  other way to stop me having to scroll all the way past one supplement to be
  able to match another's components."* An arrow and a count on every set heading.
- `[x]` **It stays folded**, per game — a fold you have to make again every
  visit is a chore, not a fold.
- `[x]` ⚠️ **A search overrules it**, or a component would hide inside a folded
  set while you were searching for it by name.
- `[x]` **6 new checks** — 219 to 225, one of which was measuring the page
  rather than the screen and was rewritten until it measured what you see.

### 23 August 2026 — a deck is counted, a counter is not

- `[x]` ⭐️ **The checklist counts a deck against its quantity.** The designer: *"build
  checklist counting deck against quantity - it's then my responsibility to
  ensure I have the correct number of cards to fill each deck. the
  game itself will do the validation of the content of those
  cards."* A line marked **all different** reads *3 of 24* and is not done
  until every card is cut; the summary also gives the sum in actual pieces,
  because a deck of twenty-four counts once as a component and is twenty-four
  evenings of cutting.
- `[x]` ⚠️ **The rule the room is built on is untouched.** *26 Damage counters*
  still wants ONE piece cut — the sheet prints one design twenty-six times and
  the game repeats it. Nothing in a printed contents list tells a quantity from
  a deck, so each line says which and the room never guesses. See CLAUDE.md 36.
- `[x]` ⚠️⚠️ **The count is asked before the guess**, which it was not at
  first: a deck of twenty-four with nothing cut read as *probably cut* because
  three pieces happened to be named after it, and the checklist showed 100%.
  Teeth tried — put the order back and two checks go red.
- `[x]` ⭐️ **A deck is where many matches are right.** *Confirm the likely
  links* ties up every piece whose name matches a deck, where for an ordinary
  component it insists on exactly one.
- `[x]` **A whole pasted list can be marked as decks** in one tick, since a
  contents list is usually all one sort at a time.
- `[x]` **10 new checks** — 209 to 219.

### 23 August 2026 — the sheet list opens on the work

- `[x]` ⭐️ **Sheets opens on *To outline*, and remembers what you choose.**
  The designer: *"the default view should be 'To outline', not 'All'. Although best if
  platform remembers the last view a user selected and goes back to that.
  Otherwise I waste time wading through lots of cut and filed sheets before I
  find my next sheet to cut."* Remembered per game, since two games are at
  different stages.
- `[x]` ⚠️ **Finished with beats nothing outlined.** *"If a sheet is marked as
  finished even though nothing needed to be cut from it (because it was all
  duplication), it shouldn't appear in the 'To outline' view."* It does not
  any more — the tick is the only thing that can know a sheet is done when it
  has no outlines on it.
- `[x]` **An empty list says why it is empty.** The commonest empty list is now
  a good one — *"Nothing left to outline in this game"*, not *"No sheet matches
  that"*.
- `[x]` **5 new checks** — 204 to 209, in a real browser, because this is
  entirely about what is in front of you when you open a game.

### 23 August 2026 — one line of a contents list, several components

- `[x]` ⭐️⭐️ **Split a checklist line into the components it really stands
  for.** The designer, on a game's supplements: *"the contents of the
  supplements only gives generic descriptions of ship cards belonging to the
  factions the supplements bring to the game"* — one line naming a player's
  movement templates where the box holds three ships, each with a name of its own.
  *"What's the best way to deal with that to ensure the game engine knows what
  it's looking at?"*
  **Split** on the row takes the real names, one a line, and the one line
  becomes three components wanted once each. Every piece linked in Match then
  gets its **own** name, which is what anything reading the manifest needs.
- `[x]` ⚠️ **It is offered, never done.** *26 damage counters* is one design
  printed twenty-six times and one row is right for it; *3 movement templates* is
  three pieces of card. Nothing but a person can tell those apart from the
  printed line, so Split sits on every row and is never used by itself. See
  CLAUDE.md 34.
- `[x]` ⭐️ **Nothing is left adrift, and nothing you typed is trodden on.** A
  piece linked to the old line follows to the first new component and the room
  says how many moved; a name the room filled in follows too; **a name you
  typed yourself is left exactly as it was.**
- `[x]` **And it pays off backwards as well:** a piece already named by hand
  is recognised by the component split out for it, so *Confirm the likely
  links* ties them together in one press.
- `[x]` **15 new checks** — 189 to 204.

### 23 August 2026 — the room explains itself

- `[x]` ⭐️⭐️ **Every button, link and box says what it does.** The designer, after two
  days of using it: *"I don't, for example, have any idea what 'straight to the
  table' means on the project selection screen, so a hover tool or just in line
  text popup or whatever explaining what all the features and buttons do would
  be very helpful. And that's not just for me, obviously!"* Point at anything
  and a plain sentence appears beside it — on the front page, the project page
  and the cutting table alike.
- `[x]` **A switch for everybody who would rather read.** *What does this do?*
  at the top writes every explanation out underneath its own control, and is
  remembered between visits. Hovering does not exist on a touch screen, and
  hunting for the one button you do not understand is not reading.
- `[x]` ⭐️ **It is a rule now, not a tidy-up.** One sentence in `data-tip` —
  or in an ordinary `title`, which the script takes over so the same words are
  never written twice — and **`check.sh` names any button that carries
  neither**. That check is the whole point: the eighty controls that existed
  were an afternoon; the next one is for ever.
- `[x]` 🖼 **The bubble was invisible on the cutting table** — it was styled in
  `room.css`, which the table does not load, being one self-contained file.
  Found by measuring it rather than believing the flag that said it was
  showing. A thing that goes on every page carries its own paint: see
  CLAUDE.md 32.
- `[x]` ⚠️ **The switch went round in circles.** It writes lines under the
  controls, and watches the page for new controls to write lines under. See
  CLAUDE.md 33.
- `[x]` **14 new checks** — 175 to 189.

### 23 August 2026 — a shape drawn once, used in any game

- `[x]` ⭐️⭐️ **Shapes kept.** The designer, on a game printed on one die: *"I will
  need to cut a number of pieces that are different, but also EXACTLY the same
  shape — I only want to create that shape mask ONCE, so the ability to save a
  highly specific shape for a project (and perhaps use that between projects —
  eg one dungeon game and another) would be very useful."* Outline one door, press **Keep
  this shape**, name it; then pick it up and **every click lays another one
  down** at the same printed size. The dotted outline under the pointer shows
  exactly where it will land, and once it has landed it is an ordinary outline
  that can be adjusted like any other.
- `[x]` ⭐️ **Kept in inches, not in one sheet's pixels.** That single decision
  is what lets a shape cross to a sheet scanned at another resolution and to
  another game entirely. The nodes and the curve are what is kept, so a shape
  comes back exactly as it was drawn rather than as a flattened tracing.
- `[x]` ⭐️ **Favourited per game, searchable between games.** The designer, the same
  day: *"I'd like to be able to favourite specific shapes on a per project
  basis but have that library searchable between projects (eg in one game I
  can review shapes I favourited in another)."* The shelf is one file
  beside the projects — not inside any of them — and each shape carries the
  list of games that have starred it. The panel shows this game's, the search
  box reaches everyone's and says which game each came out of, and a star
  brings one over **without taking it from the other**.
- `[x]` **It works offline too.** The baked page keeps its shelf in the
  browser, and has no stars, there being no project to star them for. One
  function is the only thing in the editor that knows whether there is a room
  behind the page — deliberately a branch rather than a `TABLE_PATCHES` entry,
  so `node --check` parses it in both documents (fault 13).
- `[x]` ⚠️ **Nothing sent to the shelf is believed.** A shape with two nodes,
  a node that is not a number, a shape of no size or one bigger than any sheet
  is refused with a sentence rather than written into a file every project on
  the machine then reads.
- `[x]` ⚠️ **Forgetting a shape says what goes and what does not** — it goes
  from every game, and touches no piece already outlined with it. The shelf
  holds patterns, not work.
- `[x]` ⚠️ **Keeping a shape does not put it in your hand.** It did at first,
  so the row arrived already lit and the first press on it put the shape down
  again. See CLAUDE.md 28.
- `[x]` 🖼 **The × had wrapped onto a line of its own** under every row, once
  the star made a third control in a two-column grid. Found by looking at a
  screenshot. See CLAUDE.md 29.
- `[x]` ⭐️ **The size is an offer, not a rule.** The designer: *"the size of a shape
  is agnostic, surely, as I can just scale a shape whilst retaining its
  shape?"* It is. A carried shape shows the size it will land at in two boxes
  that move together, so it cannot be squashed; type a size, or **drag the
  shape out on the sheet** like a rectangle. A dragged size is kept for the
  next one, so a run of them takes one measurement.
- `[x]` ⭐️⭐️ **A kept shape is a ruler, and that is the real prize.** The designer:
  *"Say I cut a corridor shape from [a game's] core box, that should become the
  ultimate source of truth for the exact dimensions of all [that game's] corridor
  pieces, regardless of where they come from. So when I come to cut corridor
  pieces from [an] expansion or random magazine articles,
  I can somehow ensure that they will all match the source of truth's size
  exactly?"* **Scale the sheet to this shape** works a sheet's real
  dots-per-inch back from a piece the person says *is* a known shape. Every
  measurement on that sheet is then in the game's own units, and shapes laid on
  it afterwards are identical to the ones from the box the shape came out of —
  not close, the same outline. ⚠️ The size is fixed at the **sheet**, never at
  the piece; see CLAUDE.md 30 for why the other way round is worse than
  useless. It says what it will do to the sheet and asks first, and the Scale
  panel puts it back.
- `[x]` ⭐️ **A shape from a piece already cut.** The designer: *"I should be able to
  save a shape cut from a piece already cut - or is that too difficult?"* Not
  difficult at all: the outline it was cut from is still in `outlines.json`,
  and the piece's record says which sheet and which box — so the outline is
  matched to the piece by box overlap, the same trick that keeps names on
  their pieces across a re-cut, and the line that was drawn is lifted exactly.
  **Keep the shape** sits beside every cut piece on the Pieces step. If the
  outline has been redrawn since the cut it says so, rather than guessing.
- `[x]` **43 new checks** — 132 to 175. Eighteen on the shelf's own API and
  sixteen in a real browser, the important one being a shape kept off one
  sheet, laid down twice on another, and read back **off the disk** at the
  size it was kept at.

### 22 August 2026 — the room offers a kind instead of asking for one

- `[x]` ⭐️ **Guess the kind.** The designer: *"naming is always going to be the fiddly
  bit here as it will tend to rely on 3rd party lists etc, or rules manuals
  which may be tricky to comprehend."* Every piece is already measured to the
  thousandth of an inch, so the room now offers a kind with the measurement it
  was judged on beside it — above the list for a whole run at once (*call these
  42 counters*) and under the **Kind** box for the piece being named. It
  **proposes and never decides**: nothing is filled in until somebody presses,
  a kind already set is never overwritten, and *Not now* puts it away.
- `[x]` ⭐️⭐️ **The rules were tried against a real game, and it changed two of
  them.** Run over 79 real pieces the designer had already cut and named:
  *ruler* was calling two terrain tiles rulers (long and thin, but ragged blobs —
  a ruler must be **solid**); *tile* spoke once in 79 pieces and called a turn
  template a tile, so **that rule is gone**; and the PLAYER MARKER cards were being
  passed over because a 1993 publisher did not buy standard card stock, so
  a card is now also recognised by its **proportions**, offered as the less
  certain of the two and grouped apart from the exact-size cards. It speaks
  about **28 of the 79 now and every one of the 28 is right.**
- `[x]` **The kind pays for itself twice.** Once set, the *This is the
  component…* list puts the components of that kind at the top under a heading
  of their own — part of the naming done by measurement instead of by reading
  a manual.
- `[x]` ⚠️ **A kind the Kind box could not show was being thrown away.** A
  manifest written by hand, or by an older room, may carry a kind that is not
  on the room's list: the box came up blank and the next keystroke in the form
  saved that blank over a real answer.
- `[x]` ⚠️⚠️ **check.sh could check code it was not looking at** — a stale
  compiled copy, kept on a Mac in `~/Library/Caches` where nobody would look.
  Each run gets a cache of its own now. See CLAUDE.md 26.
- `[x]` ⚠️ **A browser check was scrubbing every letter s** out of the page's
  own words before reading them. See CLAUDE.md 27.
- `[x]` **check.sh finds a python that has numpy** instead of stopping with an
  import error, since on a Mac that is often not the one `python3` means.
- `[x]` **29 new checks on the measuring**, fourteen of them about the room
  keeping quiet, plus the offer reaching the page and being taken in a real
  browser. ⭐️ Their teeth were tried and found blunt at first — see CLAUDE.md
  25.

### 22 August 2026 — the way out of the room, and a real disclaimer

- `[x]` ⭐️⭐️ **Step 6: Take it away.** The room writes a plain folder that
  anything can read — pieces as ordinary pictures **named by what they are**,
  at true printed size and the right way up; the inventory as a **spreadsheet
  and** as data, in inches **and** millimetres; a **contact sheet** of every
  piece at true size; the **checklist** to print and take to the table; and
  **cut files for a laser or craft cutter**, true size in millimetres with the
  printable sheet beside each one.
  ⚠️ **Nothing in it is shaped for any particular program.** The designer: *"the
  cutting tool should remain relatively generic - not every user is going to be
  building their own version of [a game] to play on a computer! Output format is
  important."*
- `[x]` ⚠️⚠️ **A real copyright disclaimer, and it travels with the pieces.**
  The designer: *"some kind of warning that this is personal use, copyright in all
  things you cut is not your own — a real disclaimer. Don't share cut pieces
  etc etc."* The export is exactly where it matters: up to that point the
  pieces sit in one person's folder, and after it they are a tidy, named,
  portable set that is easy to put somewhere public without thinking. So the
  notice is stated plainly **above the button**, written into the folder's
  README, put in a **COPYRIGHT.txt of its own** because a README is the first
  thing anybody stops reading, and set at the **foot of every page meant to be
  printed**. It is also at the top of README.md and ROOM.md.
- `[x]` **The printed pages carry a 25mm square**, so a scaled printout gives
  itself away before anything is cut wrong.
- `[x]` **The contact sheet has its own smaller pictures.** A real game is
  hundreds of pieces, and one page pointing at hundreds of full-resolution
  scans is fault 12 by another door.
- `[x]` ⚠️ **`hidden` did not hide.** `button` and `.btn` set `display:
  inline-block`, which beats the browser's own `[hidden]{display:none}` — so a
  button marked hidden sat there in plain sight. One rule fixes it everywhere.
- `[x]` ⚠️ **A link straight to a tab quietly landed on the wrong one.** The
  tab list was written out twice — once for showing tabs, once for reading the
  address — and the sixth tab was added to only one of them. One list now.
  Fault 14's shape for the third time.
- `[x]` ⚠️ ***Open the folder* did nothing at all off a Mac**, silently. One
  line each for Windows and Linux.
- `[x]` **13 more checks**: the folder explains itself, the piece is named by
  what it is, the turn is baked into what leaves the room, the sizes are in
  both units, the notice is in all three places, and the cut file is in
  millimetres at the sheet's true size.

### 22 August 2026 — opening and quitting, and a fault that was hiding

- `[x]` ⭐️ **The room closes from the room.** See NOW, above. The designer does not
  have to find the Terminal window any more.
- `[x]` **A launcher that is not the designer's alone** — `--install-launcher`.
- `[x]` ⚠️⚠️ **A POST no longer poisons the request after it.** *Cut this
  sheet* posts `{}` and the cut handler never read it, so those two bytes sat
  in the socket and the **next** request down that kept-alive connection was
  read starting from them — the room saw `{}GET /p/...` and answered *501
  Unsupported method*. The project page would come up blank after a cut, at
  random, depending on which connection the browser reused.
  ⭐️ **It had been there all along and was invisible**, because the room's own
  logger crashed on the error it was reporting (`send_error` logs an
  `HTTPStatus`, not a string), which killed the connection, which made the
  browser quietly try again on a clean one. Fixing the logger is what let the
  fault be seen; the check went red within the minute. Reading the body is now
  done once in `route()` for every request — fault 14's lesson, applied.
- `[x]` **`check.sh` guards both**: a POST followed by a page request on the
  same connection, and the whole close-the-room sequence. Its teeth were tried,
  not assumed — put fault 20 back and it goes red on the first check.
- `[x]` **`check.sh` keeps its screenshots when a browser check fails.** `set
  -e` was aborting the script before the line that copies them out, so the one
  instruction in the file that says *LOOK AT THEM* never had anything to show.

### 22 August 2026 — a day of the designer using it

Everything here came out of them cutting with it, in this order.

- `[x]` ⭐️ ⚠️ **Nothing in the room deletes a cut piece any more.** *"Binning a
  piece shouldn't be destructive — it should be merely to hide a piece from the
  main manifest. eg there are two identical terrain tiles. The game only needs to
  store one, even though it could be placed twice in an actual game."* A piece
  is now **set aside**: moved into `pieces/spare/`, where the hand-over does
  not look, keeping its name and everything else, staying in the list dimmed
  and marked, and going back in one press. The mark follows the piece across a
  re-cut, so a re-cut cannot resurrect the spares.
- `[x]` ⭐️ **A third answer for look-alikes: "these are variants — keep them
  all".** *"There are two different player marker cards… the platform is
  suggesting Keep this one, bin the other 2."* And twelve movement templates, one
  per player, identical but for the flag in the corner. The room had only two
  ideas about two similar pieces — duplicates to bin, or unrelated — and
  neither was true. The bar turns green, stops proposing, drops the *alike*
  flag, and each piece keeps its own id. The mark rides through a re-cut.
- `[x]` ⚠️ **Dragging a name onto a piece no longer says something went
  wrong.** The whole window is a file-drop target; three of its four handlers
  asked whether the drag carried files and the fourth did not, so a drag
  between two things on the page was taken for an import and complained after
  Match had already done the job.
- `[x]` ⚠️ **Turning a piece turns its thumbnail everywhere.** It turned the
  big picture and the Match board but not the naming list beside it, so the
  turn looked refused and got done again. Also: a quarter turn swaps width and
  height, and turned pictures were being clipped by the Match box.
- `[x]` **Choosing a component fills the name in.** Dragging did; the dropdown
  did not, so a piece linked that way stayed "(unnamed)" for ever and step 4
  never finished. One rule both ways, and it says where the name came from.
- `[x]` **The step counts refresh as you work** instead of only at load.
- `[x]` ⭐️ **Names following their pieces across a re-cut is tested at last** —
  20 checks, and it found a real fault the first time out (below).
- `[x]` ⚠️ **A name whose piece is gone is no longer left lying in wait.**
  Removing the LAST outline on a sheet renumbered nothing, so the rename map
  came out empty, so the manifest was never rewritten and the dead name stayed
  under its old number — ready to land on whatever was cut there next.
- `[x]` ⚠️ **check.sh parses the editor the room SERVES, not just the template
  on disk.** Fault 6 by a new door; see CLAUDE.md 13.

### 22 August 2026 — the ledger reads

- `[x]` **A piece's name is readable in the editor's own list.** The row was
  `swatch · number · name · 8n · 0.30 × 0.30 in · ×` in 272 pixels, and the
  name was the only part of it that could shrink, so it was the only part that
  did: every piece read `C…`. Two lines now — the name on its own, the small
  print beneath — and **a name takes as many lines as it needs**; The designer chose
  that over capping it at two, on the grounds that a name they cannot read is no
  use to them. A piece with no name says *unnamed* rather than showing a blank
  line. About sixteen pixels a row.

### 22 August 2026 — made fast enough to use

The designer, on opening it: *"it now runs VERY slowly when manipulating a sheet when
cutting, all jerky. COMPLETELY unusable."*

- `[x]` ⚠️⚠️ **The page stopped stretching itself to sixteen thousand pixels.**
  `.shell`'s grid column sized itself to the sheet rail, which lays one tab per
  sheet in a row — 161 of them. The canvas takes its size from the stage, so a
  window showing 1200 pixels was repainting a 16111-pixel picture on every
  twitch of the hand. **One frame painted in a two-second drag; 120 now.**
  The piece ledger was off the side of the screen the whole time.
- `[x]` **Only the sheet on the table is fetched.** The editor used to arm a
  picture for every sheet at load: 147MB down the wire, seven gigabytes of
  unpacked pixels. Three are held at a time now.
- `[x]` **The sheet rail scrolls, on a line of its own past a dozen sheets,
  and names the book once instead of on all thirty-nine of its tabs** — six
  tabs on the rail became thirty, and you can find a sheet on it.
- `[x]` **One repaint per frame.** A trackpad reports a drag 120 times a
  second and each report used to repaint the sheet *and* rebuild the piece
  list.
- `[x]` **The rail is put right, not rebuilt** — it used to throw away 161
  buttons and their listeners on every edit.
- `[x]` The stage **says "fetching the sheet…"** while a picture is on its way,
  instead of sitting empty as though the sheet were missing.
- `[x]` Whether the rail takes a line of its own is **measured, not guessed** —
  it moves down as soon as the tabs will not fit beside the buttons, which is
  also the point at which the buttons themselves start wrapping.
- `[x]` A **check suite** — see above.

### 21 August 2026 — the room was built

- `[x]` **Projects**, each a folder with a `project.json`, whose stores may
  point anywhere — a game's project can point them into that game's own
  repository).
- `[x]` **Import**: PDF (every page at 300dpi, one `pdftoppm` run), PNG/JPEG/
  TIFF, **.docx and .doc** (the pictures inside them, which is how fan-made
  card sets are shared), **ZIP** (opened and imported whole).
- `[x]` ⭐️ **Drag and drop**: the whole window is the target, with a curtain
  that says what it will take, and **a whole folder is walked to the bottom**.
  Dropped on the front page, the folder names the project.
- `[x]` **One row per file** while importing — waiting, reading, how many
  sheets it made, or why it could not be read. One bad file no longer stops
  the rest.
- `[x]` **Fetch one file from a link**, Google Drive share links understood;
  refuses the sign-in page a private file returns.
- `[x]` **The editor is served, and saves to the project as you draw.** The
  fault that provoked the whole room.
- `[x]` **Cut** in one press, with names following their pieces across a re-cut.
- `[x]` **Name** each piece at its printed size on a one-inch grid, with ← →
  and ⏎-saves-and-goes-on.
- `[x]` ⭐️ **Match** — drag a component's name onto the piece it is.
- `[x]` **The checklist**: every component the game should have, each *cut* /
  *probably cut* / *not yet*, with a percentage. **Optional, and it says so.**
- `[x]` **Post-cut review**: flags (no name, runs off the sheet, very small,
  mostly empty, N alike) and **look-alike detection** — 144-bit pattern hash
  plus mean colour — with *keep this one, bin the other N*.
- `[x]` **Sheet thumbnails show the whole page, margins and all**, with every
  cut piece knocked out and numbered.
- `[x]` **Five steps across the top**, each with its count and the next action
  named underneath; sheet filters and search.
- `[x]` **Hooks** — a button that runs a command in the game's own folder when
  the cutting is done.
- `[x]` ⌨️ **Typing is not a shortcut** — the editor's keys stand down inside
  any text field.
