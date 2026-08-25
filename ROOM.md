# The Cutting Room — the manual

*A local web app for cutting the components out of a board game's scanned
sheets, and for knowing how much of the game you have cut. Every screen and
every button; the walk-through is [GUIDE.md](GUIDE.md).*

Everything happens on your own machine. The room listens on `127.0.0.1`
only, fetches nothing over the network, and never sends a scan anywhere.

---

> ⭐️ **New here?** [GUIDE.md](GUIDE.md) is the walk-through — the six
> steps in order, with pictures, written for somebody who has never seen
> the room. **This** file is the reference: every screen and every button.
> Where the two disagree, believe this one.

## Starting it, and stopping it

Double-click **`Cutting Room.command`** on the Desktop. The browser opens on
the room. A terminal window opens behind it and can be ignored — it is only
where the room writes down what it is doing.

**If you have no launcher yet**, make one. You only ever do this once:

```sh
/usr/bin/python3 ~/Projects/cutting-table/cutting_room.py --install-launcher
```

That writes `Cutting Room.command` onto your Desktop, pointing at wherever you
put this folder. If you move the folder, run it again. (If a launcher is
already there and says something different, the old one is kept beside it as
`Cutting Room.command.was` — nothing is thrown away.)

**To stop the room, press *Close the Cutting Room*** at the top right of any
of its pages. You do not need to find the terminal window. The room checks
first that nothing is half-finished: if an import or a cut is still running,
or a cutting table is open somewhere with an edit that has not reached the
disk yet, it says exactly what it is waiting for and lets you decide. When it
does close, the page turns into a sign saying so.

**Nothing is lost by closing it.** Everything you have cut and named is in the
project's folder and was written there as you worked; the browser is only ever
showing you what is already on the disk.

Starting it by hand still works, and so does closing the terminal window:

```sh
/usr/bin/python3 ~/Projects/cutting-table/cutting_room.py --open
```

It needs Python with **numpy** and **Pillow** (the system `/usr/bin/python3`
on this Mac has both), and **pdftoppm** (`brew install poppler`) for PDFs.

---

## ⚠️ What you cut is not yours

Copyright in a game's artwork, its design and its words belongs to its
publisher and to the artists who made it. Cutting it up and naming the pieces
changes none of that. **Nothing that comes out of this room is yours to give
away.**

It is for use on a copy of a game you own, for your own use — replacing a piece
you have lost, playing a game you already have, keeping a record of your own
shelf. Do not put cut pieces on the internet, share them, sell them, or build
them into anything you release.

The room is a tool, like a scalpel. It gives you no rights over anything you
cut with it, and its authors are not lawyers: what counts as personal or fair
use differs from country to country, and where you stand is yours to know. The
same notice goes into every folder step 6 writes, so it travels with the pieces.

---

## The steps

### 1 · A project, one per game

Type the game's name and press **Start it**. That is the whole of it — a folder
appears in `~/Documents/Cutting Room/<name>/` and everything about that game
lives in it.

Or skip even that: **drop the game's scans on the front page** — a folder will
do — and the project makes itself, named after the folder you dropped. You can
rename it later in one field.

⚠️ **Nothing else is required to begin.** The checklist (step 5) is a way of
keeping score and can be left until you want it — or never made at all.

A game that already has a folder somewhere else (inside its own code
repository, say) is registered rather than created — the *Where do the files
come from?* panel has the box, or:

```sh
/usr/bin/python3 cutting_room.py --register /path/to/that/folder
```

### 2 · Import — drop the scans on it

⭐️ **Drop them anywhere on the page.** The whole window is the target, and a
curtain comes down while you are holding them to say what it will take. There
is no small box to find, and — the reason this matters — a file dropped on a
page that is not expecting one makes the browser **navigate away to that file**
and lose what you were doing. That cannot happen here.

| What you drop | What you get |
|---|---|
| **PDF** | every page becomes a sheet, rendered at 300 dpi |
| **PNG / JPEG / TIFF** | one sheet |
| **Word (.docx)** | every picture inside it becomes a sheet |
| **Word (.doc)**, the old binary kind | converted first (macOS `textutil`), then as above |
| **ZIP** | opened, and everything inside it imported |
| ⭐️ **A whole folder** | walked to the bottom, subfolders and all, in the order the files are named |

Each file gets a row: *waiting*, *reading*, and then how many sheets it made —
or why it could not be read. **One bad file no longer stops the rest.**
Anything that is not a kind the room reads is left alone and counted.

⭐️⭐️ **Everything dropped in one go becomes one set.** Twelve files dragged in
together are twelve sheets of one set, not twelve sets of one sheet. The set
takes its name from the folder you dropped, or from the part of the file names
they all share (`sail-01`, `sail-02` → *sail*), or failing both from the day
it arrived — and you can rename it on its heading. A single file is left
alone: it is its own set already.

⭐️ **A folder from Google Drive or Dropbox:** download it — Drive hands you a
ZIP, Dropbox and Drive for Desktop give you a real folder — and drop **that**.
One gesture, whole game. If you drop a folder on the *front* page with no name
typed, the project takes the folder's own name.

⚠️ **One file by link** is also possible (the small *…or fetch one file from a
link* panel), and a Google Drive share link is understood. It only works for a
file shared **"anyone with the link"** — a private file answers with a sign-in
*page*, and the room tells you so rather than filing the page as a sheet. A
link to a *folder* cannot work at all. **Dragging is nearly always easier.**

⭐️ **A Google Doc, Sheet or Slides link works too**, and is fetched **as a
PDF**: a document has no file to download at its own address — the link opens
the editor, and what comes back to anything else asking is the editor's own
web page — so the room asks Google to export it instead. Every page of the
document becomes a sheet, the same as any other PDF.

⭐️ **While it is fetching, there is something to watch.** The room reads the
file in pieces and says how much has arrived, out of how much where the link
says so, with a bar that fills and the seconds counting up — and if nothing it
can tell you has changed for ten seconds, it says *nothing new for 12s*, which
is the honest answer to the only question anybody asks during a wait.

⚠️ **300 dpi is the whole basis of the sizes.** A PDF at true size rendered at
300 dpi gives pieces whose inches are right by construction. A photograph or a
scan at unknown scale does not — for those, use **Measure something** in the
table's Scale panel (drag a line across anything whose real length you know)
and every size after that is anchored to it.

⭐️⭐️ **Name the box a set of sheets came out of.** Sheets are grouped by the
file they were imported from, and nobody names their scans well — so each
heading on **Sheets** carries **Name this set**. Call it *Core box*, or the
name on a supplement's lid, and everything in the room says that afterwards:
the headings, the *Show* lists on Pieces and Match, the sheet cards, and the
rail at the cutting table.

⚠️ **Nothing underneath is renamed.** A piece is named from its sheet's id and
the outlines are filed under it, so the id never changes — this is only what
the box is *called*. Empty the name and every sheet goes straight back to its
file name. A sheet you have named yourself is never touched.

⭐️⭐️ **Gathering sheets that are already in.** Sheets imported one at a time,
or before the room did this, end up in a set each. **Put these N into one
set…**, beside the search box, gathers **the sheets shown** — so the search
box is how you choose them: type *sail*, see the twelve, press once and name
them. ⚠️ Nothing is renamed and nothing is cut again: a sheet only says which
set it is in, and its id — which every piece cut from it is named after — does
not change. The same press with an **empty name** puts them back into the sets
their file names give them.

⚠️⚠️ **Remove this set** — beside it — takes the whole box out of the game.
It is the one thing in the room that really deletes, so it asks first and the
question says everything: how many sheets go, how many outlines go with them,
and that pieces already cut from them are **kept** (you are asked about those
separately). ⚠️ Getting it back is not an undo: the scans have to be imported
again. The **outlines** are kept in the room's own history under Settings, so
the work is not lost with them.

⭐️⭐️ **Put a set by for later.** A box you have imported but are not cutting
yet — an advanced rule set, a supplement for version two, sheets uploaded only
because they were to hand — takes **Put this set by** on its heading. Nothing
is deleted and nothing is hidden: the sheets stay, anything already cut from
them still counts, and the **Put by for later** chip beside the other filters
shows exactly which they are. What changes is what the room counts:

- its sheets drop out of **To outline**, so the work in front of you is work
  you mean to do;
- its components drop out of the **percentage** on the Checklist, which is the
  point — a figure that includes work you have decided not to do can never
  reach 100, so it tells you nothing.

The set is named on the Checklist too, with its own figure, and the report at
the end lists it under *Sets put by for later* rather than as anything missing.
**Bring back into the cutting** on the same heading puts every one of those
figures back. See *How complete is the cutting?* below.

⭐️ **The sheet list opens on the work still to do.** With a hundred sheets
imported, the ones already cut and filed are the ones in the way — so *Sheets*
opens on **To outline**, and whichever filter you choose is remembered for that
game. A sheet you have ticked as **finished with** drops out of it even if
nothing was ever outlined on it, which is what that tick is for: a sheet whose
pieces were all duplicates of ones you had already cut is finished, and should
not keep asking.

### 3 · Outline — at the Cutting Table

Press **Outline** on a sheet. The table opens with that sheet loaded.

| | |
|---|---|
| `T` | outline — click corner by corner, or drag to sketch freehand |
| `A` | adjust — drag nodes, band off a run of them, stretch or turn the whole piece |
| `R` `E` | rectangle, ellipse — hold shift for a square or circle |
| `Enter` | close the outline you are drawing |
| `G` | drop a cross of guides; everything snaps to them |
| `V` | step through sheet / cut / shapes |
| `[` `]` | turn the sheet a quarter, to fit a wide screen |
| `S` | lay a kept shape down — one click each, or drag out a size |
| `+` | duplicate the chosen piece, for a shape that repeats off-grid. `⌘D` does the same |
| `X` | take the chosen piece off the sheet. `⌘Z` puts it back, and nothing already cut is touched |
| `O` | work on the chosen piece **on its own** — every other outline is hidden so nothing else can be grabbed by accident. Press it again to bring them back; nothing is ever deleted |
| `⌘Z` | undo, sixty steps deep |
| `esc` | abandon what you are drawing |

**Add the suggested outlines** does the easy sheets for you. ⭐️ It throws its
own rubbish away first: a hairline crack between two counters, a speck of dirt,
a scratch across the scanner glass — anything too small or too thin to be a
piece of a board game is dropped before you are shown anything, so what arrives
is only what might be real. On cards and
counters printed on a plain ground it finds every piece exactly and there is
nothing left to draw. On terrain it is a rough start to correct — the sea
painted *inside* an island is the same blue as the sheet, so the automatic
flood walks in through a lagoon and cuts the piece in half. That is why the
outline is drawn by hand once and everything either side of it is automatic.

⭐️⭐️ **A counter comes back as a counter.** Most of what a box holds is a
plain rectangle or a plain circle, so where a piece really is one it arrives
with **four straight corners** — squared to the paper if the scan was a degree
or two crooked — or as a true circle, rather than as a traced approximation
with a node wherever the scanner wobbled. Anything else — a hexagon, a
triangle, a coastline, an oval — is traced as a curve, because a wrong regular
shape drawn over your artwork looks deliberate. The room only says the shape
where the shape says it.

⭐️ **And it follows the light.** A scan or a photograph is never evenly lit,
and the ground is measured across the sheet rather than taken as one colour —
so a dark corner is not offered to you as a piece, and its fringe is not stuck
onto the piece lying against it.

⚠️ **A counter only needs cutting ONCE.** The sheet prints twenty identical damage
counters; the game repeats one for ever. Outline one of each design.

Your work is saved into the project as you draw — the strip at the top right
says *kept in the room* — and into the browser as well, so a moment offline
costs nothing.

#### Shapes kept — draw a shape once, use it for ever

Some games are printed on one die: every door the same rectangle, every room
tile the same square, every card the same card. **Shapes kept**, on the left of
the table, is for those.

1. Outline one of them properly, and choose it.
2. Press **Keep this shape** and give it a name — *door*, *round counter*.
3. Press it in the list to pick it up (the tool changes to **Lay a shape**),
   then **click wherever each one goes**. One click, one piece. The dotted
   outline under the pointer is exactly where it will land.
4. `esc` puts it down again.

**The shape is the thing; the size is an offer.** A kept shape remembers the
size it was drawn at, in inches, and lays down at that size — usually what you
want. But you can type another size in the two boxes, or **drag the shape out**
on the sheet like a rectangle, and it scales without changing shape. Drag one
to the right size and the next click keeps it, so a run of them takes one
measurement. What is kept is the shape's nodes and its curve, so once it has
landed you can adjust it like anything you drew yourself.

#### ⭐️ One box becomes the ruler for a whole game

This is the reason to keep shapes at all. The designer, 23 August 2026: *"Say I cut a
corridor shape from [a game's] core box, that should become the ultimate source
of truth for the exact dimensions of all [that game's] corridor pieces,
regardless of where they come from."*

A sheet from an expansion, a fan PDF or a scanned magazine is at **whatever
scale it happens to be at**, and a piece cut from it will be a few per cent out
— which shows the moment you put it on the board next to a core-box piece. A
kept shape fixes that, because a shape whose true size you know is a **ruler**:

1. Cut and keep one corridor from the core box. That is the source of truth.
2. Open the new sheet, and outline one corridor on it — roughly is fine, or lay
   the kept shape over it and drag it until it covers the printed piece.
3. Pick the kept shape up and press **Scale the sheet to this shape**. The room
   works the sheet's real dots-per-inch back from the two sizes, says what it
   is about to do, and asks.
4. Now **every** size on that sheet is in the game's own units. Lay the shape
   for the rest of the corridors and they are not merely close — they are the
   same outline, to the pixel.

The Scale panel puts it back if you change your mind, and *Measure something*
still works for a sheet you have no kept shape for.

#### From a piece already cut

You do not have to be at the table. On the **Pieces** step, any cut piece has
**Keep the shape** beside it: the outline it was cut from is still on file, so
the room lifts the line that was drawn rather than tracing it back out of the
finished picture. It is exact, and it changes nothing about the piece.

**Starred for this game, searchable across all of them.** The list shows the
shapes starred for the game you are in, which is short enough to work down. The
search box goes through **every game's** shapes on the shelf — so a door drawn
for one dungeon game can be found while cutting another — and the ★
brings it over without taking it away from the game it came out of. A shape
kept while working on a game is starred for it automatically.

⚠️ The **×** forgets a shape everywhere, because the shelf is shared. It never
touches a piece already outlined with it: the shelf holds patterns, not work.

The shelf is a file of its own, `shapes.json`, **beside** the projects rather
than inside one — that is what lets every game reach it. Offline, the baked
Cutting Table keeps its shelf in the browser instead, and has no stars, because
there is no project there to star them for.

### 4 · Cut

**Cut this sheet** (at the table) or **Cut** (on the sheet card). Every
outline becomes its own PNG at full resolution, with a smoothed edge pulled
slightly inside the line so the printed die-cut mark cannot show on the
finished piece, and each is measured in inches.

Cut a sheet again after correcting an outline and the names already given to
its pieces follow them, even where adding a piece renumbers the rest.

### 5 · Name, and match

⭐️ **A game is worked through a box at a time.** The designer, 24 August 2026: *"I
don't want to go sheet by sheet, I'm much more likely to want to see core or
supplement pieces — the random sheet numbers are not
useful."* So **Pieces** gathers its pieces by **box** — the core game, each
supplement — and its *Show* list offers each box with its sheets underneath.
**Match** has the same list above its board, so it can be held to the box you
are rationalising instead of serving you the whole game. The boxes are worked
out from the sheet names, the same way the Sheets page groups them, so every
page agrees about what a box is.

⚠️ **A piece under *Not off any sheet this project knows*** is a picture
sitting in the pieces folder that the room has no record of cutting. It is not
an error — a project whose pieces folder is shared with something else (a
game's own repository, say) will have them — but if you did not expect it, that
is where to look.

⭐️ **Every list in the room folds.** A game and its supplements are one long
list, and the box you are working through is somewhere down the middle of it.
So every heading — a set of components on **Match** and on the **Checklist**, a
book of sheets on **Sheets**, a sheet's pieces on **Pieces** — has an arrow and
a count, and folds away at a press. Each stays as you leave it, per game. A
search always reaches inside a folded set, so nothing you are looking for can
hide in one.

Two ways round, and the second is usually quicker:

- **Pieces** — one piece at a time on a one-inch grid: a name, what kind of
  thing it is, a note, a quarter-turn so the printing reads upright.
  **← and →** move between pieces and **⏎ in the name box saves and goes on**,
  so naming forty-five pieces is a typing job rather than a clicking one.
- **Match** — ⭐️ **drag a component's name from the list on the left onto the
  piece it is.** The piece takes that name and the checklist ticks it off.
  Drag a piece back onto the list to undo it. Double-click a piece to open it
  on the Pieces page.

**The name and the component are not the same thing, and you need both.** The
component says *which entry on the checklist this piece answers*; the name says
*what the thing is*, and the name is what goes into the game's manifest and is
read back by the game. The checklist is optional — a game may have no component
list at all — so the name is the record that always exists. Choosing a
component, either way round, **fills the name in for you** if the piece has not
got one, and says so under the box; type over it whenever a piece needs a name
of its own.

#### The room offers a kind, so you do not have to say it

Naming is the expensive part of the whole business — a name usually comes from
somewhere outside the room, a contents list or a rules manual — so the room
takes what steps out of it that it can. It has measured every piece, and a
shape says a good deal on its own: **2.5 × 3.5in is a playing card whatever the
game is printed for.**

So above the piece list you will find something like

> **The room can see what 26 of these pieces probably are.**
> 12 pieces look like **counters** — 0.63 × 0.63 in, a small square, the size
> counters are punched at.   *[Call these 12 counters]*

One press takes a whole run of them. The same offer sits under the **Kind** box
for whichever piece you are naming, with a *Use it* beside it. Both say the
measurement they were judged on, so you can see whether to believe them.

**It offers; it never decides.** Nothing is filled in until you press, a kind
you have already set is never overwritten, and the offer goes away as soon as
you have answered it. *Not now* puts the whole thing away.

⭐️ **A round chit is offered as a counter, the same as a square one.** There
was a *token* on the list for round ones and it has been taken off, because
there is no firm difference — it varies by publisher and often by nothing at
all — and a kind you cannot choose between is a decision handed back to you by
the one part of the room whose whole job is to take decisions away. The reason
beside the offer still says which you are looking at ("0.74 in across with its
corners off"), the measurements still carry the shape, and *token* is still on
the **Kind** box if your game really does tell them apart.

**What a kind actually does**, so you know how much to care: it is the heading
a piece sits under. It groups the contact sheet, sorts the inventory
spreadsheet and fills the filter on the checklist — and nothing else. No cut,
no export and no hand-over behaves differently because of it.

It knows three things — **counters** (any small chit, square, round or
hexagonal), **cards**, and **rulers** — and it is **silent about everything
else**, on purpose. A piece
the size of a page might be a board, a chart, a player mat or the back of the
box; a two-inch square might be a floor tile or a turn template. There is no
way to tell from a measurement, so the room does not pretend there is. On the
real sheet it was tried against it spoke about 28 pieces out of 79 and
was right about all 28.

Once a kind is known it pays for itself again: the **This is the component…**
list puts the components of that same kind at the top, under a heading of their
own, so there is less of the checklist to read past.

**Turn it** is a *fixed, one-time correction*: this piece was printed sideways
on the sheet, hand it over the right way up. The hand-over bakes the turn into
the finished picture. It is **not** for turning a piece during play — a turning
template that gets spun around the table is the game's business at run time;
the room's job is only to give it to the game upright and at its true printed
size.

### After the cut — what the room noticed

The Pieces page is also the review. Each piece carries flags, and the filter
chips at the top select them:

| | |
|---|---|
| **No name** | nothing has said what it is yet |
| **N alike** | this piece and N−1 others look like the same component — unless you have said they are variants, in which case they stop being flagged |
| **Worth a look** | it runs off the edge of the sheet, or is very small, or is mostly empty — usually an outline that wants correcting |
| **Held back** | you marked it *hold back* when you named it: it is cut and named but not ready to be used yet. Each row carries the reason you gave |

⭐️ **Held back is the one you set yourself.** The other three chips are the
room's own reading of the pieces; *hold back* is a note you write on a piece
when you name it — *artwork*, *rules unclear*, *wrong scan* — saying why it is
not in play yet. It changes nothing about the piece and the piece is handed
over with the rest; it is a list to come back to. So the chip gathers them,
and the reason is printed on each row: a list of six pieces that all say
nothing but *held back* is a list you still have to open six times.

⭐️ **The end-of-job check is the way in.** Its counts of *pieces held back*
and *pieces with no name* are links: press one and the Pieces page opens with
that chip already chosen. A count you cannot open is a count you cannot act on.

⚠️ **The two do not count quite the same thing, and the list says so.** Every
chip here shows the pieces you have **set aside** along with the rest, dimmed
and labelled, because nothing on this page is ever out of sight. The printed
check counts the other way round: a piece set aside is counted as set aside and
as nothing else, so it is left out of *pieces held back* there. Rather than let
the two numbers disagree in silence, the count above the list says how many of
what it is showing are set aside — *2 pieces in all — 1 set aside*.

⭐️ **Nothing held back is the good answer**, so an empty list says which empty
it is — *Nothing is being held back here* — rather than leaving a blank page
that reads as a broken screen. Every chip does the same.

⭐️ **Every flag can be answered, including by saying it does not matter.**
Open a piece the room is worried about and the worry is written out in full,
with **That is fine** beside it. Press it and the room stops flagging that
piece for that reason — on its row and in *Worth a look* — and says instead
that you looked and waved it through, with **Flag it again** if you change your
mind. Nothing about the piece changes and nothing is cut again.

⚠️ It matters more than it sounds. *Worth a look* is a list of things to deal
with, and a flag nothing can clear means the list never empties — so after a
week it is never opened, and the next flag on it, the one that really is a bad
outline, is never seen either. A sheet scanned edge to edge will flag half its
pieces as *runs off the sheet* quite correctly and quite uselessly; wave them
through and the list is worth reading again.

The answer is written onto the piece, so it **follows it when the sheet is cut
again**, exactly as a name does.

⭐️ **Look-alikes are the useful one.** A component sheet prints twenty of each
counter and **only one is wanted** — the game repeats it for ever. Open any
piece with an *alike* flag and a bar appears with the whole set side by side,
and two answers:

- **Keep this one, set the other N aside** — they really are the same thing
  printed over and over. This is the common case and the whole economics of a
  counter sheet. ⚠️ **Nothing is deleted.** The spares are moved into a `spare`
  folder inside the pieces store, where the hand-over does not look, and they
  stay in the Pieces list, dimmed and marked *set aside*. One press puts one
  back.
- **These are variants — keep them all** — they are *different designs of one
  component*. One game has two player marker cards, so that each player has
  their own, and twelve movement templates identical but for the player's badge in
  the corner. They are not duplicates and you want all of them.

Press the second and the bar turns green: *N designs of the same component,
kept on purpose*. The room stops proposing to set them aside, the *alike* flag comes
off them, and each keeps its own id and its own picture. **The checklist still
counts the component once**, however many of the set are linked to it. There is
an undo on the bar if you change your mind.

The mark is written onto each piece, so it **follows them when the sheet is cut
again**, exactly as a name does.

⚠️ **It never sets anything aside on its own, and it should not.** Two counters
can be the same size, the same shape and the same colour and still be different
counters. The room puts them next to each other; your eye decides.

⭐️ **Judging a look-alike.** The row of pictures in *N pieces look like this
one* is there for one decision — the same piece twice, or two designs of one
component — so **hover any of them** to see that piece at full size under the
pointer, with its id and printed size. Nothing is clicked and no page is left.
The same works on the row of pictures beside a suggested kind.

⭐️ **Naming a whole deck at once.** Tick **choose several at once** above the
piece list and every row gets a tick box, with *all shown* and *none* beside
it. Tick the pieces — a filter or a box first makes that quick — choose the
component, and **Apply to the ticked pieces** gives them all the same one.
A piece that already has a name of its own keeps it; only blanks are filled.

⭐️ **A card's back is another piece.** Cut the back once — it is a piece like
any other — then set it on each card with **Its back**, or on a whole deck at
once from the *choose several* bar. A set with three different backs is simply
three pieces. The inventory names the file each back was written as.

⭐️ **Mark your backs, and the list stops being a haystack.** Set a back
piece's **Kind** to **card back** and *Its back* offers only the backs — on a
real game that is six pieces to choose from instead of two hundred. Untick
**only pieces marked as a card back** under the box to see everything again;
until you have marked any, the whole list is shown as before. Nothing guesses
this: the room cannot see the back of a card, and a wrong back applied to a
deck of thirty-two in one press is exactly the kind of confident wrong answer
it refuses to give.

⭐️ **The component list puts your box first.** *This is the component…* on a
piece cut from a supplement's sheets offers that supplement's components
first, then the rest of that box, then the same sort of thing from elsewhere,
then everything else — each band saying how many it holds. It works out which
set a box of sheets answers to from the links you have already made, so it gets
better as you go and needs nothing set up. ⚠️ It **orders**; it never hides. A
piece cut from a supplement may perfectly well be a core component that was
reprinted, and it is still there to choose.

⭐️ **How many the game needs** is for a design printed once and used many
times — the one card that appears twenty times in a deck of thirteen. You
still cut it **once**; this is what tells whatever reads the pieces to repeat
it. ⭐️ **The checklist counts it too**, so that deck of thirteen designs
reads as the full thirty-two cards rather than *13 of 32*, and says
underneath what the number is made of: *3 pieces, repeated to fill it*.
Nothing sets this by itself — the room cannot know a card is printed twenty
times — so a deck stays short until you say so.

⭐️ **Start this piece again** empties every box on the piece being viewed —
name, component, kind, use, id, turn, note — in one press, for a piece filled
in from the wrong row of a list. It asks first, and it does not touch the
picture, the outline, whether the piece is set aside, its look-alike mark, or
the flags you have waved through.

⭐️ **On the Checklist, hover the green pill** on any component counted as cut
and the piece it was counted from appears, full size. The piece names beside it
do the same.

### Setting a piece aside

⚠️ **Nothing in the room throws a cut piece away.** *Set this piece aside* — on
the look-alike bar, on the piece itself, or on the *choose several at once*
bar for a whole handful at a time — **moves** it into `pieces/spare/`.
Its name, kind, note, turn and component link are all kept, and the mark
follows the piece when the sheet is cut again, so a re-cut will not hand the
game back the nineteen duplicates you had just put away.

It is for the second copy of a thing the game only needs once: *there are two
identical terrain tiles; the game stores one, and can place it twice.* A piece set
aside stops counting as work still to do, stops being flagged as a look-alike,
and is left out of the hand-over — because the hand-over reads the pieces
folder itself and does not look inside `spare/`.

⭐️ **Several at once.** Tick **choose several at once**, tick the copies, and
**Set the ticked pieces aside** puts the lot away in one press. Tick pieces
that are already aside and the same button offers to bring them back.

⭐️ **Where the piece IS, is what the room believes.** Anything sitting in
`pieces/spare/` is set aside, whether or not anything ever wrote it down —
so a piece dropped in there by hand shows as set aside, and a mark that went
missing repairs itself the next time the Pieces list is read.

To undo it, open the piece and press **Put this piece back in play**.

**Order** re-groups the list: by sheet, by size (which clusters counters and
cards on its own), or by name (which puts everything unnamed together).

---

## The checklist — how complete is the cutting?

⭐️ **Every component belongs to a set** — the core game, or a supplement — and
everything in the room groups by them. There are two ways to make one:
**+ Add a set**, which offers the boxes of sheets you have imported by the
names you gave them (so the sheets and the components agree about what the box
is called) or a name of your own; and the **Set** column on any row, which
moves that component and can make a set on the way past. A section made before
it has anything in it sits on the list, empty, saying so.

### ⭐️ One is enough, unless every one is different

A line's quantity means one of two quite different things, and only you know
which. Under the **Qty** box each line says which the room is assuming:

- **One is enough** — the sheet prints twenty-six identical damage counters and
  the game repeats one for ever, so cutting **one** finishes the line. This is
  what the room has always assumed, and it is right for counters, markers and
  anything printed over and over.
- **All different** — a deck of twenty-four damage cards is twenty-four
  different pieces of card. The line then reads *3 of 24* and is not done until
  every one is cut.

Press the word to change it. Pasting a list has a tick for the whole list —
*these are decks* — since a contents list is usually all one sort at a time.

Two things follow. A deck is the one place where **many** name matches are
right, so *Confirm the likely links* ties up every piece whose name matches a
deck, where for an ordinary component it insists on exactly one. And the
summary gives the sum both ways: components accounted for, and — where any
deck is counted — how many **actual pieces** that is.

### ⭐️ When one line means several components

A printed contents list often sums several different components up in one
line — *3 movement templates*, *4 dungeon doors* — where the box really holds
three ships with three different names. That matters more than it looks:
until the line is broken up, Match can only give all three pieces the **same
name**, and whatever reads the pieces afterwards cannot tell them apart.

Press **Split** on the row and give the real names, one a line. The one line
becomes three components, each wanted once, each remembering the printed line
it came out of. Then every piece linked in Match gets its own name.

⚠️ **This is not the same as a quantity.** *26 damage counters* is one design
printed twenty-six times — you cut one, and one row is right. Only you know
which lines are which, so the room offers Split on every row and never uses it
by itself.

Two useful things follow. A piece already linked to the old line **follows** to
the first of the new components rather than being left pointing at nothing —
and a name **you** typed is never overwritten, only one the room filled in. And
if you had already cut and named those pieces by hand, each new component finds
its own piece, so *Confirm the likely links* ties them all up in one press.

⚠️ **Optional.** Cutting works perfectly well without one; make it when you
want to keep score.

### ⭐️⭐️ Learn the list from the pieces, when there is no contents list

Most games' contents lists are not typed out anywhere, and what a piece is
*called* is the expensive part of this whole business — it comes from a
rulebook or somebody's forum post, not from the piece. But the pieces
themselves are already cut, already measured, and the room already knows which
of them look alike. So it can build the list the other way round.

**Learn it from the pieces** (on the empty checklist, or *Learn from the
pieces* beside the other buttons) gathers every cut piece that answers to
nothing on the list into groups of the same size and design, and shows each
group with its pictures:

> **6 pieces, 4 different designs** · 0.84 × 0.84 in · looks like a counter

You give each group **one name**, and press *Add the ones I have named*. Each
group becomes a line on the checklist with its quantity filled in, and every
piece in it is tied to that line — so the score is right immediately.

- ⚠️ **A group you do not name is not added.** The room cannot know what a
  piece is called, and it does not guess. Nothing is cut, moved or renamed.
- ⭐️ **How many designs is the room's own evidence**, and it is the one thing
  a printed contents list can never tell you: twenty pieces of one design is a
  counter printed twenty times (*one is enough*), twenty pieces of twenty
  designs is a deck (*all different*). It offers the answer and you can change
  it, exactly as on any other line.
- ⭐️ **A group of several designs is numbered** — *Damage card 01, 02, 03* —
  because thirty-two pieces all called the same thing cannot be told apart by
  anything reading the folder afterwards.
- ⭐️ **A name you have already typed is offered back**, where every named
  piece in the group agrees about it.
- ⭐️ Too coarse a line can be broken up afterwards with **Split** (above).

The **Checklist** tab is the index of every component the game should have:
each counter, template, ruler, card deck, tile and chart, with the printed
quantity and which sheet it is on. Against each one:

| | |
|---|---|
| **cut ✓** | a cut piece is linked to it |
| **probably cut** | no link, but a piece's *name* matches — press **Confirm the likely links** to make them firm |
| **not yet** | nothing yet |

⭐️⭐️ **A figure for each set, and a headline over what you are cutting now.**
The work is done a box at a time, so the reading of it is too: every section
heading carries its own *12 of 30 · 40%*. The big figure at the top is over the
sets you are **cutting now** — a set you have **put by for later** (from its
heading here, or from the box's heading on Sheets: they are the same switch) is
left out of it, and the line underneath says how many components that is and
what the whole game reads. Nothing is hidden: the components stay on the list,
and anything already cut against them still counts.

Filter by kind, by group (core box / expansion / magazine) or by state, and
type in the boxes to correct a name, a quantity or a sheet reference in place.

**Building the list.** Press **Paste the contents list** and type or
paste the box's own contents list, one component a line:

```
26 Damage counters
Turning template x2
Long range ruler
9 | Large templates | template
```

A leading or trailing number becomes the quantity; the third field after a
`|` sets the kind. Everything can be edited afterwards.

⭐️⭐️ **One box at a time.** The panel asks which set the lines belong to, and
⭐️ **offers the boxes of sheets you have already named** — so paste the core
box's contents list into *Core box*, then the supplement's into the set named
after the supplement, without typing either name twice. (*+ a set of some
other name…* is there for a set that is not a box of sheets at all.)

⭐️ Picking a box that way also tells the room which set that box's pieces
answer to, so every component list puts the right box first from the very
first piece — rather than working it out from the links you have made so far. Everything in the room
groups by that set afterwards: the checklist, Match, and the end-of-job
report, which counts each box separately.

⚠️ **The tick beside it — *these are all different pieces* — is worth
understanding.** Left unticked, `26 Damage counters` means one design printed
twenty-six times and **cutting one is enough**, which is the rule the whole
room is built on. Tick it when you are pasting a page of *decks*, where all
thirty-two cards really are different and every one has to be cut. Nothing in
a printed contents list can tell those apart, so only you can say — and any
line can be changed afterwards with the *one is enough* / *all different*
button on its row.

⭐️ **A program can write this list.** It is plain JSON, and `PUT` to
`/api/p/<project>/wanted` with an `items` array replaces the lot. If whatever
you are cutting *for* already knows what the pieces should be — a game engine
that has read the rulebook, a spreadsheet, a published contents list — let it
write the list rather than typing it twice. Each item takes `id`, `name`,
`kind`, `group` (which box), `qty`, `each` (⭐️ *all different*, which is what
makes a deck count properly), `match`, `where` and `notes`.

---

## ⭐️⭐️ The check at the end — is everything really there?

On **Take it away**, above the button, is *Check the cut against the contents
list*. It is the last thing to read before the pieces leave the room, and it
is a **report**: it changes nothing at all.

It says, set by set:

- **Components with nothing cut** — the plain gaps.
- **Not enough cut yet** — *Damage cards, 24 of 32*. And it distinguishes
  *some are cut but not all* from *nothing is cut and a name merely looks
  right*, because those are worth very different amounts.
- **Counted only because a name looks right** — a **guess**. Tie the piece to
  the component, or say it is not the same thing, before trusting the total.
- ⭐️⭐️ **Decks the list counts as a single card** — read this one first. A
  deck of thirty-two counted as one piece reads as *done* the moment one card
  is cut, so the percentage above it means nothing. Set that line to *all
  different* on the Checklist and the count becomes worth reading. ⚠️ It only
  ever says this about a **deck**: `26 Damage counters` has exactly the same
  shape and is exactly right, because one design is printed twenty-six times.
- ⭐️ **Cut pieces that answer to nothing on the list** — the inverse, and the
  one nothing else can tell you. Each is either something the printed contents
  list forgot, a piece cut twice, or a piece cut from the wrong place. ⭐️ Each
  one says **how big it is**, in inches and millimetres, because a size is very
  often the whole answer: a 0.6in square is a counter, a 2.5 × 3.5in rectangle
  is a card.
- **Pieces with no name**, **pieces held back**, and **anything set aside** —
  so each of those is a decision and not an accident.
- ⭐️ **Sets put by for later** — named, with what they hold, at the end. None
  of it is counted anywhere above: not as missing, and not in the percentage.
  A report that quietly dropped a whole box would be lying by omission, so it
  says which boxes and how many components.

**Read the whole check** opens it as a page to read and to print. ⭐️ **Every
piece it names is a link** — press one and the room opens the Pieces page on
that piece, with any narrowing you had on cleared out of the way, so a finding
is something to go and deal with rather than a name to hunt for. Press the
browser's Back button to return to the report. The counts in the panel itself
work the same way: *3 pieces held back* opens the list of those three.

The same report goes into the exported folder twice:
`check-against-the-list.html` to read, and `check-against-the-list.json` for a
program — so whatever ingests the pieces has the room's own account of what is
missing instead of working it out again. ⚠️ The exported copy has **no links**
in it, on purpose: it is meant to be read by somebody with no Cutting Room
running, and a link to this computer would be a dead one in their folder.

⚠️ With no contents list it says so, plainly, rather than reporting every
piece you have as answering to nothing. The checklist is optional and this
does not quietly make it compulsory.

---

## 6 · Take it away — the way out

Press **Take it away**. The room writes a folder beside the project called
`export`, and it is a plain folder that anything can read:

| | |
|---|---|
| `pieces/` | one picture per component — an ordinary PNG with a transparent background, at full scan resolution, **named by what it is** rather than by which corner of which sheet it came off. Turned pieces come out the right way up. |
| `pieces/spare/` | the duplicates you set aside, kept rather than thrown away |
| `inventory.csv` | the whole list as a spreadsheet — opens in Numbers or Excel. Every piece with its size in inches *and* millimetres, its kind, which sheet it came off, and any note you made |
| `inventory.json` | the same list again, for a program to read |
| `contact-sheet.html` | every piece at its true printed size on one page. Open it in a browser, or print it |
| `still-to-cut.html` | the checklist, to print and take to the table with a scalpel |
| `laser/` | one pair of files per outlined sheet: a **cut file** at true size in millimetres, and the **printable sheet** to go with it |

**None of it is shaped for any particular program**, and that is deliberate.
The same folder is what a Tabletop Simulator or Tabletopia mod wants, what a
VASSAL module wants, what somebody reprinting a lost counter at true size
wants, and what somebody archiving an out-of-print box wants. Anything that
needs a special format writes that last small step on its own side — the way
a hand-over hook does, below.

### Cutting new pieces on a laser or craft cutter

The `laser/` folder has two files per sheet. Print the `-print.png` **at
100%** — not "fit to page" — stick it to your board, and load the `-cut.svg`.
The cut lines are in the sheet's own positions, so they fall exactly on the
printing. Every piece is a different colour, because LightBurn and its like
sort a job into layers by colour, so they arrive already sorted.

⚠️ **Check one measurement with a ruler before you cut anything.** The contact
sheet and the checklist both carry a 25mm square for exactly this: if it does
not measure 25mm, the printer has scaled the page and nothing on it is true
size.

⚠️ The folder is **replaced whole** every time you export, so keep nothing of
your own in it. Everything in it can be made again from the sheets and the
outlines.

---

## Hand-overs

A project can carry **hooks** — a button that runs a command in the game's
own folder when the cutting is done. A game might have two: one hands the cut
pieces to the game, the other rebuilds a proof page. They are declared in
`project.json`:

```json
"hooks": [
  {"id": "finish", "label": "Hand the cut pieces to the game",
   "cmd": ["/usr/bin/python3", "tools/finish_pieces.py"],
   "cwd": "/path/to/the/game"}
]
```

---

## ⭐️ If something goes wrong

Three things in a project cannot be rebuilt from the scans: the **outlines**
you drew, the **names** you gave the pieces, and the **checklist**. The room
keeps the last **sixty** copies of each, by itself, every time one of them is
saved — you do not have to do anything, and there is nothing to remember.

**Settings** lists them: when each was kept and what was in it (*221
components*, *79 pieces named*), with a button to put one back. The copy it
replaces is kept as well, so putting one back is not a one-way door either.

⚠️ Close the cutting table before putting **outlines** back — a table left open
will save what is on its screen over the top of them.

## Where everything lives

```
<project>/
  project.json        the project: its name, its paths, its hooks, its sheets
  sheets/             every sheet as a 300dpi PNG   (rebuildable; git-ignored)
  outlines.json       every outline on every sheet  ← THE THING TO KEEP
  masks/              one flat colour per outline, per sheet
  pieces/             every cut piece as its own PNG
  pieces/index.json   where each piece came from: sheet, box, ink
  manifest.json       what each piece IS: name, kind, note, turn, component
  wanted.json         the checklist: what the game should have

<the room's home, e.g. ~/Documents/Cutting Room/>
  projects.json       where the projects are
  shapes.json         the shelf of kept shapes, shared by every game
```

⚠️ **`outlines.json` is the file to keep.** The masks and every cut piece can
be rebuilt from it and the scans; nothing else can.

A project's `paths` may point any of those somewhere else — a game's project
can point them at that game's own `reference/` and `assets/` folders, so what is
cut in the room is exactly what the game loads.

---

## ⭐️ If you do not know what a button does, the room will tell you

Every button, link and box in the room carries a plain sentence saying what it
does. **Point at it** and the sentence appears beside it.

If you would rather read the whole page at once — or you are on a touch screen,
where there is no pointing — press **What does this do?** at the top right. Every
explanation is then written out underneath its own control, and stays that way
until you press it again. It is remembered between visits.

The cutting table has the same sentences on hover. It has no switch, because
every inch of its top bar is a tool and the sheet gets what is left.

⭐️ **This is a rule of the room, not a feature of it:** a control that does not
say what it does is a control nobody presses. Anything added here must carry its
sentence, and the checks refuse a button that does not.

## ⚠️ If a button says "no such call"

The room's **pages** are read off the disk every time you ask for one, so they
are always the newest. The room's **program** is whatever was loaded when you
opened it, and a running program cannot re-read itself. So if the Cutting Room
has been updated while it was open, you can be looking at a new button whose
answer does not exist yet.

The room notices this and says so in a band across the top of every page,
with the button that fixes it in the band: **Start the room again now**. The
room stops and starts itself in the same window at the same address, and this
page comes back by itself a few seconds later. Nothing is ever at risk:
everything cut and named is on the disk.

⭐️ **Start it again** is also in the bar at the top of every page, beside
*Close the Cutting Room*, for whenever you want it — after updating the room,
or if anything ever seems stuck.

⚠️ It asks the same question closing asks: if a cutting table is holding an
edit that has not reached the disk, it says so and waits for you, because a
restart is a close with a promise attached. And it **reads the new code before
letting go of the old room** — if that code would not start, the room says so
and stays exactly as it is, rather than going away and not coming back.

## Keyboard

At the table, single keys pick tools — but ⚠️ **only when you are not typing**.
The moment the cursor is in a name or note box, every key belongs to you and
the shortcuts stand down (Escape lets go of the box). That was not true before
21 August 2026, and typing "Treasure chest" in a name box used to change the
tool four times on the way past.

| Where | | |
|---|---|---|
| Table | `T` `A` `R` `E` | outline · adjust · rectangle · ellipse |
| Table | `G` `V` `[` `]` | guides · change the view · turn the sheet |
| Table | `S` | lay a kept shape down, one click each |
| Table | `⏎` `esc` `⌘Z` | close the outline · abandon · undo |
| Table | `+` `X` `O` | duplicate the chosen piece · take it off the sheet · work on it alone |
| Pieces | `←` `→` | the piece before / after |
| Pieces | `⏎` *in the name box* | save it and go on to the next |

## Two things that are easy to get wrong

**Colours are identity.** The cutter tells pieces apart by the colour each
outline was drawn in, so two *touching* pieces of the same colour would come
out as one. The table never hands out a colour already in use.

**Sheet ids are storage keys.** A sheet is `<prefix>-<page>` — `core-03`,
`plague-09` — and the outlines are filed under that id. Never renumber or
re-prefix a set somebody has started outlining.

---

## What must not go in this repository

Game components are copyrighted. This repository holds the **tool**, never
the sheets, never a baked page (which has the sheets inside it), and never a
cut piece. `.gitignore` is written to keep them out, and it should stay that
way.
