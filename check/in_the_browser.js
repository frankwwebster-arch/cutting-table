/* Work the Cutting Table the way a hand would, in a real browser, and say
   what is wrong in plain English.
 *
 * Run it through check/check.sh, which puts a throwaway game in front of
 * it. It needs nothing installed: Node 22 or later has a WebSocket of its
 * own, and it drives Chrome over the DevTools protocol directly.
 *
 * What it is here to catch, all of which has happened:
 *   · the work living only in the browser and never reaching the project
 *   · typing a piece's name working the single-key tools on the way past
 *   · the sheet rail stretching the page, and the canvas with it
 *   · every sheet of a game being fetched and unpacked at once
 *   · a page that is silently dead because a string was left unterminated
 */
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const CHROME = process.env.CHROME ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = Number(process.env.CDP_PORT || 9400);
const ROOM = process.env.ROOM || "http://127.0.0.1:8799";
const PROJECT = process.env.PROJECT || "proving-ground";
const OUTLINES = process.env.OUTLINES;          // the project's outlines.json
const BED = process.env.BED;                    // the project's own folder
const BAKED = process.env.BAKED;                // an offline page to try too
const SHOTS = process.env.SHOTS || "";          // where to leave screenshots
const SHEETS = Number(process.env.SHEETS || 66);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
// the box a sheet came out of, worked out the way every page in the room
// works it out — off the sheet id (fault 42)
const bookish = (sid) => (String(sid || "").match(/^(.+)-\d+$/) || [0, sid || ""])[1];

class Page {
  constructor(ws) {
    this.ws = ws; this.n = 0; this.waiting = new Map(); this.on = new Map();
    ws.addEventListener("message", (ev) => {
      const m = JSON.parse(ev.data);
      if (m.id && this.waiting.has(m.id)) {
        const { ok, bad } = this.waiting.get(m.id);
        this.waiting.delete(m.id);
        m.error ? bad(new Error(JSON.stringify(m.error))) : ok(m.result);
      } else if (m.method && this.on.has(m.method)) {
        this.on.get(m.method).forEach((f) => f(m.params));
      }
    });
  }
  send(method, params = {}) {
    const id = ++this.n;
    return new Promise((ok, bad) => {
      this.waiting.set(id, { ok, bad });
      this.ws.send(JSON.stringify({ id, method, params }));
      setTimeout(() => { if (this.waiting.delete(id)) bad(new Error("no answer to " + method)); }, 45000);
    });
  }
  listen(method, fn) {
    if (!this.on.has(method)) this.on.set(method, []);
    this.on.get(method).push(fn);
  }
  async val(expr) {
    const r = await this.send("Runtime.evaluate", { expression: expr, returnByValue: true });
    if (r.exceptionDetails) {
      const e = r.exceptionDetails;
      throw new Error("the page threw: " +
        ((e.exception && e.exception.description) || e.text));
    }
    return r.result.value;
  }
  async go(url) {
    const there = new Promise((ok) => this.listen("Page.loadEventFired", ok));
    await this.send("Page.navigate", { url });
    await there;
    await sleep(2500);
  }
  async press(key) {
    // a named key (Escape) carries no text, and Chrome refuses the event if
    // it is given one; a letter must carry it or nothing is typed
    const named = key.length > 1;
    await this.send("Input.dispatchKeyEvent", named
      ? { type: "rawKeyDown", key, windowsVirtualKeyCode: key === "Escape" ? 27 : 0 }
      : { type: "keyDown", text: key, unmodifiedText: key, key });
    await this.send("Input.dispatchKeyEvent", { type: "keyUp", key });
  }
  async type(text) { for (const ch of text) await this.press(ch); }
  /* ⚠️ A MOVE WITH A BUTTON NAMED ON IT IS A DRAG, NOT A HOVER. `mouse`
     below names the left button because everything else here is dragging
     something; Chrome then treats the move as part of a drag and the page
     never sees the pointer arrive. Hovering needs a move with no button at
     all. */
  async hover(x, y) {
    await this.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: x, y: y });
  }
  async mouse(type, x, y, buttons) {
    await this.send("Input.dispatchMouseEvent",
      { type, x, y, button: "left", buttons, clickCount: type === "mouseMoved" ? 0 : 1 });
  }
  async shot(name) {
    if (!SHOTS) return;
    const png = await this.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(SHOTS, name), Buffer.from(png.data, "base64"));
  }
}

const done = [];
function check(what, right, saw) {
  done.push({ what, right: !!right });
  console.log((right ? "  ok   " : "  WRONG ") + what +
              (saw === undefined ? "" : "   — saw " + JSON.stringify(saw)));
}

async function open() {
  const profile = fs.mkdtempSync(path.join(require("os").tmpdir(), "cutting-check-"));
  const chrome = spawn(CHROME, [
    "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--window-size=1500,1050",
    `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "about:blank",
  ], { stdio: ["ignore", "ignore", "ignore"] });
  for (let i = 0; i < 120; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const p = list.find((t) => t.type === "page" && t.webSocketDebuggerUrl);
      if (p) {
        const ws = new WebSocket(p.webSocketDebuggerUrl);
        await new Promise((ok, bad) => { ws.addEventListener("open", ok); ws.addEventListener("error", bad); });
        return { page: new Page(ws), chrome, profile };
      }
    } catch (e) { /* not up yet */ }
    await sleep(200);
  }
  chrome.kill("SIGKILL");
  throw new Error("Chrome never answered. Set CHROME to where it lives.");
}

/* What the page looks like, measured rather than guessed at. */
const SHAPE = `(function () {
  var cv = document.getElementById("cv");
  var over = [];
  Array.prototype.forEach.call(document.querySelectorAll("*"), function (el) {
    if (el.getBoundingClientRect().width > innerWidth + 4) {
      over.push(el.tagName.toLowerCase() + (el.id ? "#" + el.id : "." + String(el.className).split(" ")[0]));
    }
  });
  var mid = cv.getContext("2d").getImageData(Math.round(cv.width / 2), Math.round(cv.height / 2), 6, 6).data;
  var lit = 0;
  for (var i = 3; i < mid.length; i += 4) if (mid[i] > 0) lit++;
  var led = document.querySelector(".ledger");
  return {
    pageW: document.documentElement.scrollWidth, innerW: innerWidth,
    tooWide: over.slice(0, 5),
    canvasW: cv.width, canvasH: cv.height,
    canvasMB: +(cv.width * cv.height * 4 / 1e6).toFixed(1),
    tabs: document.querySelectorAll(".tab").length,
    runs: Array.prototype.map.call(document.querySelectorAll(".tabs .grp"), function (g) { return g.textContent; }),
    firstTab: (document.querySelector(".tab b") || {}).textContent,
    ledgerSeen: !led || led.getBoundingClientRect().right <= innerWidth + 1,
    inked: lit,
    fetched: performance.getEntriesByType("resource")
      .filter(function (r) { return /\\/sheet\\//.test(r.name); }).length
  };
})()`;

(async () => {
  const { page, chrome, profile } = await open();
  const thrown = [];
  try {
    await page.send("Page.enable");
    await page.send("Runtime.enable");
    page.listen("Runtime.exceptionThrown", (p) => thrown.push(
      String((p.exceptionDetails.exception && p.exceptionDetails.exception.description) || p.exceptionDetails.text)));
    page.listen("Runtime.consoleAPICalled", (p) => {
      if (p.type === "error") thrown.push("console.error " + p.args.map((a) => a.value ?? a.description).join(" "));
    });
    // the cut asks whether to go and name the pieces; say no and stay here
    const asked = [];
    let answer = "a kept shape";     // what a prompt is answered with
    let agree = false;               // and whether a confirm is agreed to
    page.listen("Page.javascriptDialogOpening", async (p) => {
      asked.push(p.message);
      try {
        // A confirm is answered NO so the page stays where it is. A prompt is
        // asking for a name, and refusing one only proves nothing happens.
        await page.send("Page.handleJavaScriptDialog",
          { accept: p.type === "prompt" || agree, promptText: answer });
      } catch (e) { /* gone */ }
    });

    // ---------------------------------------------------- the served table
    console.log("\nthe table, served by the room");
    await page.go(`${ROOM}/p/${PROJECT}/table`);
    const s = await page.val(SHAPE);
    check("the page is no wider than the window", s.pageW <= s.innerW + 1,
          { pageW: s.pageW, stretchedBy: s.tooWide });
    check("the canvas is the size of the stage, not of the page",
          s.canvasW < s.innerW && s.canvasMB < 12, { size: [s.canvasW, s.canvasH], MB: s.canvasMB });
    check("every sheet has a tab", s.tabs === SHEETS, s.tabs);
    check("a run of sheets is named once, and numbered within it",
          s.runs.length >= 1 && s.firstTab === "p.1", { runs: s.runs, firstTab: s.firstTab });
    check("the piece ledger is on the screen", s.ledgerSeen);
    check("the sheet is drawn", s.inked > 0, s.inked);
    check("only the sheet on the table was fetched", s.fetched === 1, s.fetched);

    // ---------------------------------------------------- draw, name, keep
    console.log("\ncutting a piece out, and keeping it");
    const st = await page.val(`(function(){ var r = document.getElementById("cv").getBoundingClientRect();
      return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`);
    await page.press("r");                       // Rectangle
    const a = { x: st.x + st.w * 0.42, y: st.y + st.h * 0.40 };
    const b = { x: st.x + st.w * 0.58, y: st.y + st.h * 0.58 };
    await page.mouse("mousePressed", a.x, a.y, 1);
    for (let i = 1; i <= 12; i++) {
      await page.mouse("mouseMoved", a.x + (b.x - a.x) * i / 12, a.y + (b.y - a.y) * i / 12, 1);
    }
    await page.mouse("mouseReleased", b.x, b.y, 0);
    await sleep(600);
    check("the rectangle is on the piece list",
          (await page.val(`document.querySelectorAll("#pieces .piece").length`)) === 1);

    // ⚠️ TYPING IS NOT A SHORTCUT. Every letter of this name is also a tool:
    // T outline, E ellipse, A adjust, R rectangle.
    const NAME = "Trebuchet Ellipse Adjust";
    await page.val(`document.getElementById("pieceName").focus(); true`);
    await page.type(NAME);
    await sleep(400);
    const typed = await page.val(`(function () { return {
      value: document.getElementById("pieceName").value,
      focus: document.activeElement.id,
      pieces: document.querySelectorAll("#pieces .piece").length,
      onList: (document.querySelector("#pieces .piece .nm") || {}).textContent }; })()`);
    check("the name box got every letter", typed.value === NAME, typed.value);
    check("the name box kept the cursor", typed.focus === "pieceName", typed.focus);
    check("typing made no new pieces and lost none", typed.pieces === 1, typed.pieces);
    check("the piece list shows the name", typed.onList === NAME, typed.onList);

    if (OUTLINES) {
      // ⚠️ THE WORK MUST NOT LIVE IN THE BROWSER. It goes to the project a
      // moment after the last edit, and that file is what the cut is made
      // from. Four sheets of outlining were once lost to this.
      await sleep(1500);
      const book = JSON.parse(fs.readFileSync(OUTLINES, "utf8"));
      const sid = Object.keys(book.sheets || {})[0];
      const kept = sid ? (book.sheets[sid].pieces || []) : [];
      check("the outline reached the project's own file", kept.length === 1, { sheet: sid, pieces: kept.length });
      check("its name went with it", kept[0] && kept[0].name === NAME, kept[0] && kept[0].name);
    }
    check("the page says the work is kept",
          /kept in the room/.test(await page.val(`document.getElementById("roomState").textContent`)));

    // ---------------------------------------------------- away, and back
    console.log("\nleaving the sheet and coming back to it");
    await page.val(`document.querySelectorAll(".tab")[5].click(); true`);
    await sleep(1200);
    check("another sheet starts empty",
          (await page.val(`document.querySelectorAll("#pieces .piece").length`)) === 0);
    check("changing sheet fetches that sheet and no others",
          (await page.val(`performance.getEntriesByType("resource").filter(function(r){return /\\/sheet\\//.test(r.name);}).length`)) === 2);
    await page.val(`document.querySelectorAll(".tab")[0].click(); true`);
    await sleep(1200);
    const back = await page.val(`(function(){ return {
      rows: document.querySelectorAll("#pieces .piece").length,
      name: (document.querySelector("#pieces .piece .nm") || {}).textContent }; })()`);
    check("the work is still there on the way back", back.rows === 1 && back.name === NAME, back);
    check("and its picture is drawn again", (await page.val(SHAPE)).inked > 0);
    await page.shot("table.png");

    // ---------------------------------------------------- cut it out
    if (BED) {
      console.log("\ncutting the piece off the sheet");
      asked.length = 0;
      await page.val(`document.getElementById("roomCut").click(); true`);
      for (let i = 0; i < 60 && !asked.length; i++) await sleep(500);
      check("the cut says what it made", /1 piece cut from/.test(asked[0] || ""), asked[0]);

      const index = JSON.parse(fs.readFileSync(path.join(BED, "pieces", "index.json"), "utf8"));
      const ids = Object.keys(index.pieces || {});
      check("one piece is in the index", ids.length === 1, ids);
      if (ids.length) {
        const one = index.pieces[ids[0]];
        // the demo sheet is 6 x 8 inches at 300dpi and the rectangle was
        // drawn across about a sixth of it, so the piece should come out at
        // a size a person would recognise rather than a stray pixel or the
        // whole page
        const inches = [+(one.w / 300).toFixed(2), +(one.h / 300).toFixed(2)];
        check("it comes out at a printed size a person would recognise",
              inches[0] > 0.2 && inches[0] < 6 && inches[1] > 0.2 && inches[1] < 8, { id: ids[0], inches });
        check("it says which sheet it came off", one.sheet === "proving-ground-sheets-01", one.sheet);
        check("its picture is on disk",
              fs.existsSync(path.join(BED, "pieces", ids[0] + ".png")), ids[0] + ".png");
      }
    }

    // ------------------------------------ a shape kept, and laid down again
    // ⭐️ the designer, 23 August 2026, on a game printed on one die: "I will need to cut a
    // number of pieces that are different, but also EXACTLY the same shape —
    // I only want to create that shape mask ONCE." The shape is kept off one
    // sheet and laid down on ANOTHER one, twice, because that crossing is the
    // whole feature: what is kept is inches, not this sheet's pixels.
    if (OUTLINES) {
      console.log("\nkeeping a shape, and laying it down on another sheet");
      answer = "Proving door";
      asked.length = 0;
      // a shape drawn in ANOTHER game, so the crossing between them can be
      // tried rather than argued about
      await fetch(`${ROOM}/api/shapes`, { method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ what: "keep", project: "another-game",
          game: "A Dungeon Game",
          shape: { name: "quest door", curve: false, w: 1.5, h: 1.5,
                   pts: [[0, 0], [1.5, 0], [1.5, 1.5], [0, 1.5]] } }) });
      await page.val(`document.querySelector("#pieces .piece").click(); true`);
      await page.val(`document.getElementById("shapeKeep").click(); true`);
      await sleep(1200);
      const shelved = await page.val(`(function () { return {
        rows: document.querySelectorAll("#shelf .kept").length,
        says: (document.querySelector("#shelf .kept .dim") || {}).textContent,
        name: (document.querySelector("#shelf .kept b") || {}).textContent,
        drawn: !!document.querySelector("#shelf .kept canvas") }; })()`);
      check("the shape is on the shelf, under the name given for it",
            shelved.rows === 1 && shelved.name === "Proving door", shelved);
      check("with a drawing of it, and the size it will land at",
            shelved.drawn && /\d\.\d\d × \d\.\d\d in/.test(shelved.says || ""), shelved.says);

      // the shelf is the ROOM's, not this page's: it is on disk already
      const shapes = (await (await fetch(`${ROOM}/api/shapes`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ what: "list" }) })).json()).shapes || [];
      check("and the room has it, not just the browser", shapes.length === 2,
            shapes.map((s) => s.name));

      // ⭐️ FAVOURITED PER GAME, SEARCHABLE ACROSS THEM. The designer, 23 August
      // 2026: "in [one game] I can review shapes I favourited in [another]
      // project."
      // The other game's door is on the same shelf and must NOT be in the
      // way here until it is asked for by name.
      check("only this game's shapes are in the list",
            shelved.rows === 1 && /1 kept for this game, of 2/.test(
              await page.val(`document.getElementById("shelfSays").textContent`)),
            await page.val(`document.getElementById("shelfSays").textContent`));
      await page.val(`(function () { var f = document.getElementById("shapeFind");
        f.value = "quest"; f.dispatchEvent(new Event("input")); return true; })()`);
      await sleep(200);
      const found = await page.val(`(function () { return {
        rows: document.querySelectorAll("#shelf .kept").length,
        name: (document.querySelector("#shelf .kept b") || {}).textContent,
        says: (document.querySelector("#shelf .kept .dim") || {}).textContent,
        starred: (document.querySelector("#shelf .kept .star") || {})
                   .getAttribute("aria-pressed") }; })()`);
      check("searching reaches a shape drawn in another game",
            found.rows === 1 && found.name === "quest door", found);
      check("and says which game that was, before it is laid down here",
            /A Dungeon Game/.test(found.says || ""), found.says);
      check("it is not one of this game's yet", found.starred === "false", found.starred);
      await page.val(`document.querySelector("#shelf .kept .star").click(); true`);
      await sleep(600);
      await page.val(`(function () { var f = document.getElementById("shapeFind");
        f.value = ""; f.dispatchEvent(new Event("input")); return true; })()`);
      await sleep(200);
      check("a star brings it over to this game's own list",
            (await page.val(`document.querySelectorAll("#shelf .kept").length`)) === 2);
      const stars = ((await (await fetch(`${ROOM}/api/shapes`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ what: "list" }) })).json()).shapes || [])
        .filter((x) => x.name === "quest door")[0] || {};
      check("without taking it away from the game it came out of",
            (stars.stars || []).length === 2, stars.stars);

      // a different sheet, which has nothing on it at all
      await page.val(`document.querySelectorAll(".tab")[7].click(); true`);
      await sleep(1200);
      const empty = await page.val(`document.querySelectorAll("#pieces .piece").length`);
      await page.val(`document.querySelector("#shelf .kept .pick").click(); true`);
      await sleep(300);
      const carrying = await page.val(`(function () { return {
        tool: document.getElementById("tLay").getAttribute("aria-pressed"),
        lit: !!document.querySelector("#shelf .kept.on") }; })()`);
      check("picking a shape up arms the tool and lights the shape",
            carrying.tool === "true" && carrying.lit, carrying);

      const sp = await page.val(`(function(){ var r = document.getElementById("cv").getBoundingClientRect();
        return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`);
      const spots = [{ x: sp.x + sp.w * 0.35, y: sp.y + sp.h * 0.30 },
                     { x: sp.x + sp.w * 0.62, y: sp.y + sp.h * 0.66 }];
      for (const at of spots) {
        await page.mouse("mouseMoved", at.x, at.y, 0);
        await page.mouse("mousePressed", at.x, at.y, 1);
        await page.mouse("mouseReleased", at.x, at.y, 0);
        await sleep(350);
      }
      const laid = await page.val(`document.querySelectorAll("#pieces .piece").length`);
      check("one click lays one down, and the next lays another",
            empty === 0 && laid === 2, { before: empty, after: laid });
      check("and nothing was asked but the shape's name", asked.length === 1, asked.length);
      await page.shot("shapes-kept.png");

      await sleep(1500);
      const book = JSON.parse(fs.readFileSync(OUTLINES, "utf8"));
      const on = book.sheets["proving-ground-sheets-08"] || { pieces: [] };
      check("both reached the project's own file", on.pieces.length === 2,
            on.pieces.length);
      const kept = shapes[0] || {};
      const sizes = (on.pieces || []).map((pc) => {
        const xs = pc.pts.map((q) => q[0]), ys = pc.pts.map((q) => q[1]);
        return [+((Math.max(...xs) - Math.min(...xs)) / 300).toFixed(2),
                +((Math.max(...ys) - Math.min(...ys)) / 300).toFixed(2)];
      });
      // ⭐️ THE SIZE IS THE POINT. A shape kept in inches must land at the
      // size it was kept at, or it is no use across sheets, let alone games.
      check("each one landed at the printed size it was kept at",
            sizes.length === 2 && sizes.every((s) =>
              Math.abs(s[0] - kept.w) < 0.02 && Math.abs(s[1] - kept.h) < 0.02),
            { kept: [kept.w, kept.h], landed: sizes });
      check("and they landed where each was put, not on top of one another",
            on.pieces.length === 2 &&
            Math.abs(on.pieces[0].pts[0][0] - on.pieces[1].pts[0][0]) > 30,
            on.pieces.map((pc) => pc.pts[0]));

      // ⭐️ THE SIZE IS AN OFFER, NOT A RULE. The designer, 23 August 2026: "the size
      // of a shape is agnostic, surely, as I can just scale a shape whilst
      // retaining its shape?" So it can be laid at another size, and the
      // shape must not be distorted by the change.
      const kw = kept.w, kh = kept.h;
      await page.val(`(function () { var f = document.getElementById("layW");
        f.value = "${(kw * 2).toFixed(2)}"; f.dispatchEvent(new Event("input")); return true; })()`);
      await sleep(200);
      check("typing a width moves the height with it, so the shape is kept",
            Math.abs((await page.val(`+document.getElementById("layH").value`))
                     - kh * 2) < 0.02,
            await page.val(`document.getElementById("layH").value`));
      await page.mouse("mouseMoved", spots[0].x, spots[0].y + 40, 0);
      await page.mouse("mousePressed", spots[0].x, spots[0].y + 40, 1);
      await page.mouse("mouseReleased", spots[0].x, spots[0].y + 40, 0);
      await sleep(1600);
      const grown = JSON.parse(fs.readFileSync(OUTLINES, "utf8"))
        .sheets["proving-ground-sheets-08"].pieces;
      check("and it lands at the size asked for", grown.length === 3, grown.length);
      if (grown.length === 3) {
        const pc = grown[2];
        const xs = pc.pts.map((q) => q[0]), ys = pc.pts.map((q) => q[1]);
        const w = (Math.max(...xs) - Math.min(...xs)) / 300;
        const h = (Math.max(...ys) - Math.min(...ys)) / 300;
        check("twice as wide, twice as tall, the same shape",
              Math.abs(w - kw * 2) < 0.03 && Math.abs(h - kh * 2) < 0.03,
              { asked: [+(kw * 2).toFixed(2), +(kh * 2).toFixed(2)],
                landed: [+w.toFixed(2), +h.toFixed(2)] });
      }

      // ⭐️⭐️ THE SHAPE AS THE SOURCE OF TRUTH FOR A GAME. The designer, 23 August
      // 2026: a corridor cut from a game's core box "should become the
      // ultimate source of truth for the exact dimensions of all [that game's]
      // corridor pieces, regardless of where they come from". A kept shape is
      // something whose true size is known, which is exactly what setting a
      // sheet's scale needs — so it can tell a sheet from anywhere what its
      // dots per inch really are.
      const before = await page.val(`document.getElementById("scaleNow").textContent`);
      asked.length = 0;
      // ⚠️ it asks before it changes every measurement on a sheet, so this
      // has to say yes — and that IT ASKS is one of the things checked
      agree = true;
      await page.val(`document.getElementById("layScale").click(); true`);
      await sleep(900);
      agree = false;
      const after = await page.val(`document.getElementById("scaleNow").textContent`);
      // The piece on the table is the one just laid at TWICE the kept size.
      // If it really IS that shape, then an inch of it takes twice as many
      // pixels as the sheet was assuming — so 300 dpi becomes 600.
      check("a kept shape can tell the sheet what its scale really is",
            /(59|60)\d dpi/.test(after), { was: before, now: after });
      check("and it says what it will do to the sheet before doing it",
            asked.length === 1 && /dpi/.test(asked[0] || ""), asked[0]);
      await page.val(`document.getElementById("scaleOff").click(); true`);
      await sleep(900);
      check("and it can be put back", /300 dpi/.test(
            await page.val(`document.getElementById("scaleNow").textContent`)));

      await page.press("Escape");
      await sleep(200);
      check("escape puts the shape down again",
            !(await page.val(`!!document.querySelector("#shelf .kept.on")`)));
    }

    // ⭐️ A SHAPE OFF A PIECE ALREADY CUT. The designer, 23 August 2026: "I should be
    // able to save a shape cut from a piece already cut - or is that too
    // difficult?" It is not: the outline it was cut from is still on file, so
    // the line that was drawn is lifted rather than traced back out of the
    // picture.
    if (BED) {
      console.log("\nkeeping the shape of a piece that was already cut");
      answer = "Off a cut piece";
      asked.length = 0;
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await page.val(`document.querySelector(".prow").click(); true`);
      await sleep(900);
      await page.val(`document.getElementById("fShape").click(); true`);
      await sleep(1200);
      const shelf = (await (await fetch(`${ROOM}/api/shapes`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ what: "list" }) })).json()).shapes || [];
      const off = shelf[0] || {};
      check("the shape of a cut piece goes on the shelf", off.name === "Off a cut piece",
            shelf.map((x) => x.name));
      // the piece was cut from a rectangle drawn 1.51 x 1.43in
      check("at the size the piece was cut at, off the outline that made it",
            Math.abs((off.w || 0) - 1.51) < 0.03 && Math.abs((off.h || 0) - 1.43) < 0.03,
            [off.w, off.h]);
      check("and it is one of this game's from the start",
            (off.stars || []).indexOf(PROJECT) >= 0, off.stars);
    }

    // ⭐️ AND IN THE BROWSER: the explanation has to actually appear. The designer
    // asked for "a hover tool or just in line text popup or whatever"; both
    // are here, and both are checked, because a tip nobody can see is the
    // same as no tip at all — which is exactly what happened first time out,
    // when the bubble came up unstyled and a page wide at the bottom of the
    // cutting table, switched on and invisible.
    {
      console.log("\ndoes a control explain itself when you point at it?");
      // ⚠️ back to the table first: the section before this one left the
      // browser on the project page, and a check that points at a control
      // which is not there tests nothing and stops everything after it
      await page.go(`${ROOM}/p/${PROJECT}/table`);
      const at = await page.val(`(function () {
        var e = document.getElementById("tLay"); if (!e) return null;
        var r = e.getBoundingClientRect();
        return { x: r.x + r.width / 2, y: r.y + r.height / 2 }; })()`);
      await page.mouse("mouseMoved", at.x, at.y, 0);
      await sleep(800);
      const tip = await page.val(`(function () {
        var b = document.querySelector(".tipbubble");
        if (!b) return { none: true };
        var r = b.getBoundingClientRect(), c = getComputedStyle(b);
        return { on: b.classList.contains("on"), text: b.textContent.slice(0, 30),
                 fixed: c.position === "fixed", w: Math.round(r.width),
                 seen: r.width > 60 && r.width < 520 && r.height > 10 }; })()`);
      check("pointing at a tool explains it", tip.on && /Put down a shape/.test(tip.text || ""), tip.text);
      check("and the explanation is a bubble beside it, not a strip across the page",
            tip.fixed && tip.seen, { fixed: tip.fixed, width: tip.w });
    }

    // ------------------------------------- the room's own pages, after a cut
    if (BED) {
      // ⚠️ THE DESIGNER, 22 August 2026: dragging a component's name onto a piece
      // "always seems to serve an error code (even though it also appears to
      // work!)". The whole window is a file-drop target so that a dropped PDF
      // cannot navigate the page away; dragenter and dragover asked whether
      // the drag carried FILES and the drop handler did not, so a drag from
      // one thing on the page to another was taken for an import, found no
      // files, and complained — after Match had already done the job.
      /* ⭐️ THE SHEET LIST OPENS ON THE WORK, AND REMEMBERS. The designer, 23 August
         2026: "the default view should be 'To outline', not 'All'… Otherwise
         I waste time wading through lots of cut and filed sheets before I
         find my next sheet to cut. Also if a sheet is marked as finished even
         though nothing needed to be cut from it (because it was all
         duplication), it shouldn't appear in the 'To outline' view." */
      console.log("\nthe sheet list opens on what is still to do");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const opened = await page.val(`(function () { return {
        on: (document.querySelector("#sFilter button.on") || {}).textContent,
        cards: document.querySelectorAll(".sheets .sheet").length }; })()`);
      check("a game opens on the sheets still to outline, not on all of them",
            /To outline/.test(opened.on || ""), opened.on);

      // one sheet has been outlined and cut by the checks above, so it must
      // not be in the way any more
      const shown = await page.val(`Array.prototype.map.call(
        document.querySelectorAll(".sheets .sheet .body > b"),
        function (e) { return e.textContent; }).join(" | ")`);
      check("and the sheet already outlined is not among them",
            !/proving-ground-sheets p\.1\b/.test(shown || ""),
            (shown || "").slice(0, 70));

      // ⚠️ a sheet ticked as finished with is not still to outline, even
      // though nothing was ever outlined on it — all it held was duplicates
      await fetch(`${ROOM}/api/p/${PROJECT}/sheet/second-book-of-tests-01`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ done: true }) });
      const wasThere = await page.val(`document.querySelectorAll(".sheets .sheet").length`);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const nowThere = await page.val(`document.querySelectorAll(".sheets .sheet").length`);
      check("a sheet ticked as finished with drops out of the work still to do",
            nowThere === wasThere - 1, { was: wasThere, now: nowThere });

      // and the choice is remembered, per game
      await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f="cut"]');
        b.click(); return true; })()`);
      await sleep(400);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const remembered = await page.val(`(document.querySelector("#sFilter button.on") || {}).textContent`);
      check("and the one you choose is the one you come back to",
            /Cut/.test(remembered || "") && !/To outline/.test(remembered || ""), remembered);
      // put it back, so nothing after this is looking at a filtered list
      await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f=""]');
        b.click(); return true; })()`);
      await sleep(300);

      /* ⭐️ AN EMPTY LIST MUST SAY WHY IT IS EMPTY. Now that a game opens on
         the work still to do, the commonest way to see an empty list is a
         GOOD one — there is nothing left — and "No sheet matches that" would
         read as though something had gone wrong. This also puts the finished
         tick back, so nothing after it is looking at a game in a state these
         checks invented. */
      await fetch(`${ROOM}/api/p/${PROJECT}/sheet/second-book-of-tests-01`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ done: false }) });
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f="done"]');
        b.click(); return true; })()`);
      await sleep(400);
      const emptySays = await page.val(`(function () { return {
        cards: document.querySelectorAll(".sheets .sheet").length,
        says: (document.querySelector("#sheets .note") || {}).textContent || "" }; })()`);
      check("an empty list says why it is empty, in its own words",
            emptySays.cards === 0 &&
            /No sheet has been ticked as finished with yet/.test(emptySays.says),
            emptySays);
      await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f=""]');
        b.click(); return true; })()`);
      await sleep(300);

      // ⭐️ and the switch that writes every explanation out, for a touch
      // screen and for anybody who would rather read the room than poke at it
      console.log("\nthe switch that explains everything on the page");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const before = await page.val(`document.querySelectorAll(".tipline").length`);
      await page.val(`document.getElementById("tipsToggle").click(); true`);
      await sleep(600);
      const after = await page.val(`(function () { return {
        lines: document.querySelectorAll(".tipline").length,
        says: document.getElementById("tipsToggle").textContent,
        first: (document.querySelector(".tipline") || {}).textContent }; })()`);
      check("nothing is written out until it is asked for", before === 0, before);
      check("and then every control has its sentence under it", after.lines > 10, after.lines);
      check("and the switch says how to put them away", /Hide/.test(after.says || ""), after.says);
      // ⚠️ it writes lines, and it watches the page for changes — the first
      // version answered its own writing for ever, eight times a second
      await sleep(1500);
      check("and it does not go round in circles writing them again",
            (await page.val(`document.querySelectorAll(".tipline").length`)) === after.lines);

      console.log("\ndragging a name onto a piece, in Match");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=match`);
      const cells = await page.val(`document.querySelectorAll(".mcell").length`);
      check("the cut piece is on the Match board", cells >= 1, cells);
      asked.length = 0;
      await page.val(`(function () {
        var c = document.querySelector(".mcell");
        if (!c) return false;
        var dt = new DataTransfer();
        dt.setData("text/plain", "nothing-real");   // a name, not a file
        c.dispatchEvent(new DragEvent("drop",
          { dataTransfer: dt, bubbles: true, cancelable: true }));
        return true; })()`);
      await sleep(1500);
      check("a name dropped on a piece raises no complaint of its own",
            asked.length === 0, asked);

      /* ⭐️ EVERY LIST IN THE ROOM FOLDS. The designer, 23 August 2026: first "in
         Match, it would be very helpful to be able to collapse sections eg
         for [the] Core Box, [a supplement, another supplement]… Or just some
         other way to stop me having to scroll all the way past one supplement
         to be able to match another's components", and then "I want the same
         ability to collapse and expand core/expansions/extras etc throughout
         the platform (eg in Checklist, sheets, match, pieces etc)".

         ⚠️ There is ONE mechanism, so these checks are as much about the four
         lists agreeing with each other as about any one of them working. */
      console.log("\nfolding a set away, on every list that has sets");
      for (const [group, text] of [["core", "Core one\nCore two"],
                                   ["plague", "Plague one\nPlague two\nPlague three"]]) {
        await fetch(`${ROOM}/api/p/${PROJECT}/wanted/import`, { method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, group }) });
      }

      /* What a person can actually see: a heading, and the rows under it that
         are not hidden. Counting rows that are IN the page proves nothing —
         a folded row is still in the document, which is exactly the mistake
         the first version of this check made. */
      const LOOK = (list, rows) => `(function () {
        var heads = document.querySelectorAll("${list} .fold");
        var seen = Array.prototype.filter.call(document.querySelectorAll("${rows}"),
          function (e) { return e.offsetParent !== null; });
        return { heads: heads.length, open: Array.prototype.map.call(heads,
                   function (h) { return h.getAttribute("aria-expanded"); }),
                 counts: Array.prototype.map.call(heads,
                   function (h) { return h.dataset.foldN; }),
                 arrows: Array.prototype.map.call(heads,
                   function (h) { return (h.querySelector(".arrow") || {}).textContent; }),
                 rows: seen.length }; })()`;

      const LISTS = [
        { what: "Match", tab: "match", list: "#mList", rows: "#mList .mitem" },
        { what: "the Checklist", tab: "wanted", list: "table.wanted", rows: "table.wanted tbody tr:not(.ghead)" },
        { what: "the Pieces list", tab: "pieces", list: "#plist", rows: "#plist .prow" },
        { what: "the Sheets list", tab: "sheets", list: "#sheets", rows: "#sheets .sheet" },
      ];
      for (const L of LISTS) {
        await page.go(`${ROOM}/p/${PROJECT}/?tab=${L.tab}`);
        if (L.tab === "sheets") {
          // the sheet filter is remembered, and these checks want the lot
          await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f=""]');
            if (b) b.click(); return true; })()`);
          await sleep(400);
        }
        const before = await page.val(LOOK(L.list, L.rows));
        // ⚠️ how many sets there are depends on the game in front of it —
        // this throwaway one has sixty-six sheets in three books but only one
        // piece cut, so demanding two sets everywhere would only be checking
        // the fixture. What must be true on every list is that each set has a
        // heading, it says how many are under it, and it starts open.
        check(`${L.what} gives each set a heading that can be folded`,
              before.heads >= 1 && before.open.every((o) => o === "true") &&
              before.counts.every((n) => +n > 0), { on: L.what, ...before });
        await page.val(`document.querySelectorAll("${L.list} .fold")[0].click(); true`);
        await sleep(350);
        const shut = await page.val(LOOK(L.list, L.rows));
        check(`${L.what} folds one away, and its heading stays to open it again`,
              shut.open[0] === "false" && shut.arrows[0] === "\u25b8" &&
              shut.rows === before.rows - (+before.counts[0]) &&
              shut.heads === before.heads,
              { on: L.what, was: before.rows, now: shut.rows,
                folded: before.counts[0], arrow: shut.arrows[0] });
        // ⭐️ a fold you have to make again every visit is a chore, not a fold
        await page.go(`${ROOM}/p/${PROJECT}/?tab=${L.tab}`);
        if (L.tab === "sheets") {
          await page.val(`(function () { var b = document.querySelector('#sFilter button[data-f=""]');
            if (b) b.click(); return true; })()`);
          await sleep(400);
        }
        const later = await page.val(LOOK(L.list, L.rows));
        check(`${L.what} is still folded when you come back to it`,
              later.rows === shut.rows && later.open[0] === "false",
              { on: L.what, rows: later.rows, open: later.open[0] });
        await page.val(`document.querySelectorAll("${L.list} .fold")[0].click(); true`);
        await sleep(350);
      }

      /* ⚠️⚠️ A SET IS NOT "THE ROWS THAT HAPPEN TO SIT TOGETHER". The designer, 23
         August 2026: "on #pieces the collapse/expand mechanic is going awry,
         just not working correctly, seems to be segmenting the core box over
         and over."

         Every list used to start a heading whenever the group changed from
         the row before, which only groups anything if the rows are already
         together. A piece FILE the index knows nothing about — anything else
         living in the pieces folder, and a project whose store points into a
         game's own repository — has no sheet at all, and pieces are sorted by their
         own name, so one such file lands inside a sheet's run and cuts it in
         two. Worse than untidy: both halves then carry the same fold id, so
         each claims all the rows and folding one hides the other's. */
      const strays = ["zz_no_index_at_all", "core_of_nothing"];
      for (const stray of strays) {
        fs.copyFileSync(path.join(BED, "pieces", "proving_ground_sheets_p01_00.png"),
                        path.join(BED, "pieces", stray + ".png"));
      }
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const shredded = await page.val(`(function () {
        var heads = Array.prototype.map.call(document.querySelectorAll("#plist .fold"),
          function (h) { return h.dataset.foldName; });
        var counts = Array.prototype.map.call(document.querySelectorAll("#plist .fold"),
          function (h) { return +h.dataset.foldN; });
        return { heads: heads, counts: counts,
                 twice: heads.length !== new Set(heads).size,
                 rows: document.querySelectorAll("#plist .prow").length }; })()`);
      check("a piece the index knows nothing about does not shred the list",
            !shredded.twice, shredded.heads);
      check("and it is gathered under a heading that says what it is",
            shredded.heads.some((h) => /Not off any sheet/.test(h)), shredded.heads);
      check("with every row counted once, under one heading",
            shredded.counts.reduce((a, b) => a + b, 0) === shredded.rows,
            { counts: shredded.counts, rows: shredded.rows });
      // ⚠️ take them away again: everything after this counts the pieces
      for (const stray of strays) fs.unlinkSync(path.join(BED, "pieces", stray + ".png"));

      // and the same fault on the lists made of components: one added by hand
      // goes on the END of the list, whatever set it belongs to
      await fetch(`${ROOM}/api/p/${PROJECT}/wanted/import`, { method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "Core three, added later", group: "core" }) });
      for (const [tab, sel] of [["wanted", "table.wanted .fold"], ["match", "#mList .fold"]]) {
        await page.go(`${ROOM}/p/${PROJECT}/?tab=${tab}`);
        const heads = await page.val(`Array.prototype.map.call(
          document.querySelectorAll("${sel}"), function (h) { return h.dataset.foldName; })`);
        check(`a component added later does not give ${tab} the same set twice`,
              heads.length === new Set(heads).size, heads);
      }

      /* ⚠️⚠️ ANYTHING THAT ADDS A ROW MUST OPEN THE SET IT LANDS IN. The designer,
         24 August 2026: "BUG - adding a new component does not work, so far
         as I can tell - I just tried to create a new Reward
         counter, typed in the name, clicked add, and nothing happened." It
         had worked: the component was on the disk and in the table. It landed
         in a set they had folded, so the row they were watching for was hidden the
         moment it appeared. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=wanted`);
      const shutFirst = await page.val(`(function () {
        var h = document.querySelectorAll("table.wanted .fold")[0];
        h.click();
        return h.dataset.foldHead; })()`);
      await sleep(400);
      answer = "Reward counter";
      asked.length = 0;
      await page.val(`(function () { var g = document.getElementById("wGroup");
        g.value = ${JSON.stringify("")}; return true; })()`);
      await page.val(`document.getElementById("wAdd").click(); true`);
      await sleep(1500);
      const added = await page.val(`(function () {
        var rows = Array.prototype.filter.call(
          document.querySelectorAll("table.wanted tbody tr:not(.ghead)"),
          function (r) { return r.offsetParent !== null; });
        var mine = rows.filter(function (r) {
          var i = r.querySelector('input[data-k="name"]');
          return i && i.value === "Reward counter"; });
        return { seen: mine.length, shownRows: rows.length,
                 hidden: document.querySelectorAll("table.wanted tbody tr[hidden]").length }; })()`);
      check("a component added into a folded set is not hidden by the fold",
            added.seen === 1 && added.hidden === 0, { ...added, folded: shutFirst });
      // put the list back as the other checks expect it (removing asks first)
      agree = true;
      await page.val(`(function () {
        var rows = document.querySelectorAll("table.wanted tbody tr:not(.ghead)");
        for (var i = 0; i < rows.length; i++) {
          var inp = rows[i].querySelector('input[data-k="name"]');
          if (inp && inp.value === "Reward counter") {
            rows[i].querySelector("[data-del]").click(); return true; }
        }
        return false; })()`);
      await sleep(900);
      agree = false;

      // ⚠️ but a search must not hide what it is finding
      await page.go(`${ROOM}/p/${PROJECT}/?tab=match`);
      await page.val(`document.querySelectorAll("#mList .fold")[1].click(); true`);
      await sleep(300);
      await page.val(`(function () { var f = document.getElementById("mFind");
        f.value = "plague"; f.dispatchEvent(new Event("input")); return true; })()`);
      await sleep(400);
      const found = await page.val(`Array.prototype.filter.call(
        document.querySelectorAll("#mList .mitem"),
        function (e) { return e.offsetParent !== null; }).length`);
      check("a search reaches inside a folded set rather than hiding what it finds",
            found === 3, found);
      await page.val(`(function () { var f = document.getElementById("mFind");
        f.value = ""; f.dispatchEvent(new Event("input")); return true; })()`);
      await sleep(300);
      await page.val(`document.querySelectorAll("#mList .fold")[1].click(); true`);
      await sleep(300);

      // ⚠️ AND: "I often have to rotate a piece … but the thumbnail should
      // update also, everywhere." A turn is kept in the manifest and never
      // baked into the cut PNG, so every picture of a piece has to apply it.
      console.log("\nturning a piece turns its picture everywhere");
      const first = (await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json()).pieces[0];
      await fetch(`${ROOM}/api/p/${PROJECT}/manifest/${first.stem}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rotate: 90, name: "a piece on its side" }),
      });
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const turns = await page.val(`(function () {
        function t(sel) {
          var im = document.querySelector(sel);
          return im ? (im.style.transform || getComputedStyle(im).transform) : null;
        }
        return { row: t(".prow .pic img") }; })()`);
      check("the piece's row in the naming list is turned with it",
            /rotate\(90deg\)|matrix\(0,\s*1,\s*-1,\s*0/.test(turns.row || ""), turns);
      /* ⭐️ THE ROOM OFFERS A KIND RATHER THAN ASKING FOR ONE. The designer, 22
         August 2026: "naming is always going to be the fiddly bit here as it
         will tend to rely on 3rd party lists etc, or rules manuals which may
         be tricky to comprehend." The measurement rules are checked on their
         own in check/guessing_the_kind.py; what is checked HERE is the part
         that only a browser can see — that the offer is on the page, that it
         says what it was judged on, and that pressing it puts the kind on the
         piece. */
      console.log("\nthe room offering a kind, and it being taken");
      // ⚠️ The rectangle drawn above comes out an inch and a half square, and
      // that is exactly a shape the room refuses to guess about — so it gets
      // checked for its SILENCE, and a counter is dropped in beside it to
      // press the offer on. The counter is taken away again below, before
      // anything else looks at the store.
      const quiet = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      check("the room says nothing about a piece whose shape settles nothing",
            quiet.pieces.every((p) => !p.guess),
            quiet.pieces.map((p) => [p.w_in, p.h_in, (p.guess || {}).kind]));
      const spare = path.join(BED, "pieces", "zz_a_counter.png");
      fs.copyFileSync(process.env.COUNTER, spare);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      // the list opens on its first piece, which is the drawn rectangle — the
      // offer beside the name box belongs to whichever piece is being named
      await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_a_counter"]');
        if (r) r.click(); return !!r; })()`);
      await new Promise((r) => setTimeout(r, 400));
      // ⚠️ THE BACKSLASHES BELOW ARE DOUBLED ON PURPOSE. These expressions go
      // to the browser as text inside a template literal, and a template
      // literal eats one level of escape: a `\s` written here arrives as a
      // plain "s", so `replace(/\s+/g, " ")` became replace(/s+/g, " ") and
      // scrubbed every letter s out of the page's own words before they were
      // read. It went unnoticed because two of the three checks passed anyway.
      const offer = await page.val(`(function () {
        var grp = document.querySelector(".guessbar .grp");
        var one = document.querySelector("#fKindGuess .kguess");
        return { bar: !!document.querySelector(".guessbar"),
                 said: grp ? grp.textContent.replace(/\\s+/g, " ").trim() : null,
                 button: grp ? grp.querySelector("button").textContent : null,
                 beside: one ? one.textContent.replace(/\\s+/g, " ").trim() : null }; })()`);
      check("a kind is offered for a piece whose size does settle it", offer.bar, offer.said);
      check("and the offer says what it was judged on",
            /\bin\b/.test(offer.said || ""), offer.said);
      check("and the same offer sits under the Kind box being named",
            /Looks like/.test(offer.beside || ""), offer.beside);
      await page.val(`document.querySelector(".guessbar .grp button").click()`);
      await new Promise((r) => setTimeout(r, 900));
      const kinded = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const got = kinded.pieces.filter((p) => p.stem === "zz_a_counter")[0] || {};
      check("pressing it puts the kind on the piece",
            (got.data || {}).kind === "counter", (got.data || {}).kind);
      const gone = await page.val(`(function () {
        return { bar: !!document.querySelector(".guessbar .grp") }; })()`);
      check("and the room stops asking about it", !gone.bar);
      await page.shot("guessed.png");
      // and take the counter away again, manifest entry and all, so the store
      // is exactly as the checks after this one expect to find it
      await fetch(`${ROOM}/api/p/${PROJECT}/manifest/zz_a_counter`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "" }),
      });
      fs.unlinkSync(spare);

      /* ⭐️ A LOOK-ALIKE IS NO USE AT FORTY-SIX PIXELS. The designer, 23 August 2026:
         "if platform is suggesting '[n] pieces look like this one' it's
         incredibly difficult to see them in the tiny viewport it provides -
         can you make them appear larger/preview on hover (I don't want to
         click away to another page) just to make it easier to see if there is
         any differentiation?" They are being asked whether two pieces are the
         same design and given a stamp to answer it from.

         Two copies of one piece make a look-alike pair, dropped into the
         store for this one section and taken away again at the end of it —
         the same trick as the counter above, so nothing else ever sees them. */
      const twins = ["zz_twin_a", "zz_twin_b"].map(function (n) {
        var to = path.join(BED, "pieces", n + ".png");
        fs.copyFileSync(path.join(BED, "pieces", "proving_ground_sheets_p01_00.png"), to);
        return to;
      });
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_twin_a"]');
        if (r) r.click(); return !!r; })()`);
      await sleep(700);
      const bar = await page.val(`(function () {
        var im = document.querySelector(".dupbar .pics img");
        if (!im) return null;
        var r = im.getBoundingClientRect();
        return { w: Math.round(r.width), h: Math.round(r.height),
                 big: im.getAttribute("data-big"),
                 title: im.getAttribute("title"),
                 cap: im.getAttribute("data-bigcap") }; })()`);
      check("the look-alikes are shown big enough to tell apart",
            bar && bar.w >= 80 && bar.h >= 80, bar && [bar.w, bar.h]);
      // ⚠️ the FULL picture, not the thumbnail it is standing on: a thumbnail
      // blown up is exactly as useless as a thumbnail
      check("and each offers the piece's own full picture to look at",
            bar && /\/piece\//.test(bar.big || "") && !/piece-thumb/.test(bar.big || ""),
            bar && bar.big);
      // ⚠️ and carries no title, or tips.js would put a text bubble over it
      check("with no tooltip to fight the picture", bar && !bar.title, bar && bar.title);

      /* ⚠️ BRING IT ONTO THE SCREEN BEFORE POINTING AT IT. The first version
         of this measured the thumbnail where it sat — 1496 pixels down a
         963-pixel window — and dispatched a hover into empty space, then
         reported that the preview does not work. The page was fine. */
      const box = await page.val(`(function () {
        var im = document.querySelector(".dupbar .pics img");
        im.scrollIntoView({ block: "center" });
        var r = im.getBoundingClientRect();
        return { x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) }; })()`);
      await page.hover(box.x, box.y);
      await sleep(500);
      const peek = await page.val(`(function () {
        var b = document.querySelector(".bigpeek");
        if (!b) return null;
        var im = b.querySelector("img"), r = im.getBoundingClientRect();
        return { on: b.classList.contains("on"), w: Math.round(r.width),
                 h: Math.round(r.height), src: im.getAttribute("src"),
                 cap: b.querySelector("span").textContent }; })()`);
      check("hovering one shows it far larger, without leaving the page",
            peek && peek.on && Math.max(peek.w, peek.h) >= 200, peek);
      // it names whichever of the look-alikes is under the pointer, and how
      // big that one prints — the two things you are comparing them on
      check("and the preview says which piece it is, and how big it prints",
            peek && peek.cap.indexOf((peek.src || "").split("/").pop().replace(".png", "")) === 0 &&
            /\d+(\.\d+)? × \d+(\.\d+)? in/.test(peek.cap || ""),
            peek && peek.cap);
      await page.hover(box.x, Math.max(2, box.y - 400));
      await sleep(400);
      check("and it goes when the pointer does",
            !(await page.val(`(function () { var b = document.querySelector(".bigpeek");
              return !!b && b.classList.contains("on"); })()`)));
      /* ⭐️ THE BOARD CAN BE HELD TO ONE BOX. The designer, 24 August 2026: "in
         Match, I should have the option to limit the display when
         de-selecting the tickbox 'only pieces with no component yet' to
         pieces cut from either core or one of the supplements… otherwise
         I get served with 200+ objects from across the whole game when I'm
         just trying to rationalise one supplement or something." It could only
         be narrowed one SHEET at a time, and a supplement is thirty sheets. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=match`);
      await page.val(`(function () { var u = document.getElementById("mUn");
        u.checked = false; u.dispatchEvent(new Event("change")); return true; })()`);
      await sleep(600);
      const boxes = await page.val(`(function () {
        var sel = document.getElementById("mSheet");
        return { books: Array.prototype.map.call(sel.querySelectorAll("optgroup"),
                   function (g) { return g.label; }),
                 whole: Array.prototype.filter.call(sel.options, function (o) {
                   return o.value.indexOf("book:") === 0; }).map(function (o) { return o.value; }),
                 all: document.querySelectorAll(".mcell").length }; })()`);
      check("the board can be held to a whole box, not only to one sheet",
            boxes.whole.indexOf("book:proving-ground-sheets") >= 0, boxes.whole);
      check("and each box is offered with its sheets under it",
            boxes.books.indexOf("proving-ground-sheets") >= 0, boxes.books);

      async function boardWith(v) {
        await page.val(`(function () { var s = document.getElementById("mSheet");
          s.value = ${JSON.stringify(v)}; s.dispatchEvent(new Event("change")); return true; })()`);
        await sleep(500);
        return page.val(`document.querySelectorAll(".mcell").length`);
      }
      /* ⭐️ AND THE PIECES LIST WORKS IN BOXES TOO. The designer, 24 August 2026:
         "the Pieces view is now pretty useless, and very frustrating to use.
         I don't want to go sheet by sheet, I'm much more likely to want to
         see core or supplement pieces - the random sheet
         numbers are not useful." A hundred and sixty sheet numbers are not a
         list anybody can choose from. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const byBox = await page.val(`(function () {
        var sel = document.getElementById("pSheet");
        return { order: document.getElementById("pOrder").value,
                 heads: Array.prototype.map.call(document.querySelectorAll("#plist .fold"),
                   function (h) { return h.dataset.foldName; }),
                 whole: Array.prototype.filter.call(sel.options, function (o) {
                   return o.value.indexOf("book:") === 0; }).map(function (o) { return o.value; }),
                 groups: Array.prototype.map.call(sel.querySelectorAll("optgroup"),
                   function (g) { return g.label; }) }; })()`);
      check("the pieces list gathers by box, not by sheet number",
            byBox.order === "book" &&
            byBox.heads.indexOf("proving-ground-sheets") >= 0, byBox);
      check("and it can be shown a whole box at a time",
            byBox.whole.indexOf("book:proving-ground-sheets") >= 0 &&
            byBox.groups.indexOf("proving-ground-sheets") >= 0, byBox.whole);
      // ⚠️ a piece off no sheet the room knows is a loose end, and goes last
      check("with anything off no known sheet at the end, not the front",
            byBox.heads[byBox.heads.length - 1] === "Not off any sheet this project knows",
            byBox.heads);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=match`);

      // ⭐️ the two look-alikes above came off no sheet at all, so they are
      // exactly what a box filter must leave behind — the point of the whole
      // thing is that the board stops showing you the rest of the game
      const inBook = await boardWith("book:proving-ground-sheets");
      check("choosing a box shows what was cut from it, and nothing else",
            inBook > 0 && inBook < boxes.all, { box: inBook, whole: boxes.all });
      await boardWith("");


      /* ⭐️ THIRTY-TWO CARDS, ONE COMPONENT, ONE PRESS. The designer, 24 August 2026:
         "I'd like a bulk apply function - if I can select all 32 cards in a
         deck, I should be able to apply the correct card deck label to them
         all in one go."
         ⚠️ Only the two look-alikes are ticked here, on purpose: a check that
         ticks everything would name the pieces the checks after it are
         looking at. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      // one of them is named by hand first — a bulk apply must not tread on it
      await fetch(`${ROOM}/api/p/${PROJECT}/manifest/zz_twin_b`, { method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "I typed this myself" }) });
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await page.val(`document.getElementById("pChooseOn").click(); true`);
      await sleep(700);
      const ticked = await page.val(`(function () {
        var n = 0;
        ["zz_twin_a", "zz_twin_b"].forEach(function (st) {
          var r = document.querySelector('.prow[data-stem="' + st + '"] .tick');
          if (r) { r.click(); n++; }
        });
        return { ticks: document.querySelectorAll(".prow .tick").length, hit: n,
                 says: document.getElementById("pChosenN").textContent }; })()`);
      check("pieces can be ticked to be dealt with together",
            ticked.ticks > 0 && ticked.hit === 2 && /2 pieces ticked/.test(ticked.says),
            ticked);
      const applied = await page.val(`(function () {
        var sel = document.getElementById("pChooseWanted");
        var at = -1;
        Array.prototype.forEach.call(sel.options, function (o, i) {
          if (o.textContent.indexOf("Core one") === 0) at = i; });
        if (at < 0) return "no component to apply";
        sel.selectedIndex = at;
        // ⚠️ and a back at the same time, which must not disturb the component
        var b = document.getElementById("pChooseBack");
        if (b.options.length > 1) b.selectedIndex = 1;
        return sel.value; })()`);
      agree = true;
      await page.val(`document.getElementById("pApply").click(); true`);
      await sleep(1800);
      agree = false;
      const bulked = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const twinA = bulked.pieces.filter((p) => p.stem === "zz_twin_a")[0] || {};
      const twinB = bulked.pieces.filter((p) => p.stem === "zz_twin_b")[0] || {};
      check("and one press gives them all the same component",
            (twinA.data || {}).wanted === applied && (twinB.data || {}).wanted === applied,
            [(twinA.data || {}).wanted, (twinB.data || {}).wanted, applied]);
      check("an unnamed one takes the component's name",
            (twinA.data || {}).name === "Core one", (twinA.data || {}).name);
      // ⚠️ THE CAREFUL ONE, and the same rule as everywhere else in the room
      check("and a name somebody typed themselves is left exactly as it was",
            (twinB.data || {}).name === "I typed this myself", (twinB.data || {}).name);
      /* ⭐️ A CARD'S BACK IS ANOTHER PIECE. The designer, 24 August 2026: "when I'm in
         the process of cutting a deck of cards, how do I set the correct back
         to them? Note that it's not always the same back within the same
         set." Cut the back once, point the whole deck at it in one press. */
      check("and a whole deck can be given its back in the same press",
            !!(twinA.data || {}).back && (twinA.data || {}).back === (twinB.data || {}).back,
            [(twinA.data || {}).back, (twinB.data || {}).back]);

      /* ⚠️⚠️ SETTING A PIECE ASIDE HALF WORKED, WHICH IS WORSE THAN NOT
         WORKING. The designer, 24 August 2026: "setting pieces aside seems pretty
         temperamental — I just tried to get rid of multiple copies of [one
         piece], but didn't seem to work, either in bulk when suggested, or
         individually when selected in #pieces."
         The file moved every time; the MARK was written only onto pieces the
         manifest already knew — and a duplicate you want rid of is exactly
         the piece nobody has bothered to name. So the room went on drawing it
         as though it were in play. This piece is named by nothing, which is
         the whole point of it. */
      const loose = path.join(BED, "pieces", "zz_aside.png");
      fs.copyFileSync(process.env.SPECK, loose);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const bulkAside = await page.val(`(function () {
        var on = document.getElementById("pChooseOn");
        on.checked = true; on.dispatchEvent(new Event("change"));
        var r = document.querySelector('.prow[data-stem="zz_aside"]');
        if (!r) return "no row";
        r.scrollIntoView({ block: "center" });
        var t = r.querySelector("input.tick");
        if (!t) return "no tick";
        t.click();
        var b = document.getElementById("pAside");
        return { says: b.textContent, off: b.disabled }; })()`);
      check("several pieces can be set aside at once, from the same bar that names them",
            bulkAside && bulkAside.off === false &&
            /Set the ticked pieces aside/.test(bulkAside.says || ""), bulkAside);
      await page.val(`document.getElementById("pAside").click(); true`);
      await sleep(2000);
      const put = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const one = put.pieces.filter((p) => p.stem === "zz_aside")[0] || {};
      // ⚠️ THE FAULT ITSELF: the mark, on a piece that had no entry to put it on
      check("a piece nothing has ever named is written down as set aside",
            !!(one.data || {}).spare, one.data);
      check("and the file really is in the spare folder, not deleted",
            fs.existsSync(path.join(BED, "pieces", "spare", "zz_aside.png")) &&
            !fs.existsSync(loose));
      check("while the piece itself stays on the list, dimmed, rather than vanishing",
            await page.val(`(function () {
              var r = document.querySelector('.prow[data-stem="zz_aside"]');
              return !!r && /aside/.test(r.className) && /set aside/.test(r.textContent); })()`));
      // ⭐️ and the same button the other way round, as on the piece itself
      const backAgain = await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_aside"]');
        var t = r && r.querySelector("input.tick");
        if (!t) return "no tick";
        t.click();
        return document.getElementById("pAside").textContent; })()`);
      check("and ticking pieces that are already aside offers to bring them back",
            /Put the ticked pieces back/.test(backAgain || ""), backAgain);
      await page.val(`document.getElementById("pAside").click(); true`);
      await sleep(2000);
      const home = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const two = home.pieces.filter((p) => p.stem === "zz_aside")[0] || {};
      check("one press brings them back into play, mark and all",
            !(two.data || {}).spare && fs.existsSync(loose), two.data);

      /* ⭐️ THE FOLDER IS THE TRUTH; THE MARK IS THE RECORD OF IT. Three of the
         designer's pieces were sitting in the spare folder with nothing written
         down about them, from before the fault above was found — so what the
         room reads is made to agree with where the piece actually is. */
      fs.renameSync(loose, path.join(BED, "pieces", "spare", "zz_aside.png"));
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const adopted = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const three = adopted.pieces.filter((p) => p.stem === "zz_aside")[0] || {};
      check("a piece put in the spare folder by hand is taken as set aside",
            !!(three.data || {}).spare, three.data);
      // ⚠️ take the bench back exactly as it was: put the piece back in play,
      // which is also what takes its manifest entry away, and then the file
      await fetch(`${ROOM}/api/p/${PROJECT}/pieces/aside`, { method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stems: ["zz_aside"], aside: false }) });
      fs.unlinkSync(loose);
      await page.val(`(function () { var on = document.getElementById("pChooseOn");
        on.checked = false; on.dispatchEvent(new Event("change")); return true; })()`);

      /* ⭐️ EVERYTHING A PIECE HAS BEEN CALLED, TAKEN OFF IT. The designer, 24 August
         2026: "give me a single button when viewing any single piece to
         remove all the metadata (name, component, kind etc) - just strip back
         to all those fields being unfilled." */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_twin_a"]');
        if (r) r.click(); return !!r; })()`);
      await sleep(700);
      agree = true;
      await page.val(`document.getElementById("fClear").click(); true`);
      await sleep(1500);
      agree = false;
      const wiped = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const bare = wiped.pieces.filter((p) => p.stem === "zz_twin_a")[0] || {};
      check("one press empties every box on a piece",
            !Object.keys(bare.data || {}).length, bare.data);
      check("and the piece itself is still there to fill in again",
            !!bare.stem, bare.stem);

      /* ⭐️ THE GREEN TICK SHOWS WHAT IT IS VOUCHING FOR. The designer, 24 August
         2026: "if a piece has been marked as cut with a green tick… can you
         make it appear on hover over the green CUT pill?" */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=wanted`);
      const pill = await page.val(`(function () {
        var t = document.querySelector("table.wanted .tag.cut, table.wanted .tag.part");
        if (!t) return null;
        t.scrollIntoView({ block: "center" });
        var r = t.getBoundingClientRect();
        return { big: t.getAttribute("data-big"),
                 x: Math.round(r.x + r.width / 2), y: Math.round(r.y + r.height / 2) }; })()`);
      check("a component counted as cut offers the piece it was counted from",
            pill && /\/piece\//.test(pill.big || ""), pill && pill.big);
      if (pill) {
        await page.hover(pill.x, pill.y);
        await sleep(600);
        check("and hovering the pill shows that piece, without leaving the list",
              await page.val(`(function () { var b = document.querySelector(".bigpeek");
                return !!b && b.classList.contains("on"); })()`));
        await page.hover(pill.x, Math.max(2, pill.y - 300));
        await sleep(300);
      }

      /* ⭐️⚠️ EVERY WORRY THE ROOM RAISES MUST HAVE AN ANSWER. The designer, 24 August
         2026: "some of the pieces I've cut are flagged as RUNS OFF THE SHEET.
         That's a reasonable thing to flag, but I don't see a way to remove
         that flag (because it doesn't matter), and I don't mind about the
         overrun." A flag nothing can clear means Worth a look never empties,
         so it stops being read — and the next flag on it, the one that really
         is a bad outline, is never seen either.

         A speck of a piece, 0.2in square, is "very small" by any reading. It
         is the same trick as the counter above: dropped into the store for
         this one section and taken away again at the end of it. */
      const speck = path.join(BED, "pieces", "zz_speck.png");
      fs.copyFileSync(process.env.SPECK, speck);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      const worried = await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_speck"]');
        if (!r) return null;
        r.scrollIntoView({ block: "center" });
        var chip = r.textContent.indexOf("very small") >= 0;
        r.click();
        return { chip: chip }; })()`);
      await sleep(800);
      const worry = await page.val(`(function () {
        var b = document.querySelector(".worries .waive");
        if (!b) return null;
        var line = b.parentElement.querySelectorAll("span");
        return { k: b.dataset.k, says: line[1] ? line[1].textContent : "",
                 button: b.textContent, tip: b.getAttribute("data-tip") || "" }; })()`);
      check("a piece the room is worried about wears the worry on its row",
            worried && worried.chip, worried);
      check("and the piece itself offers an answer to it",
            worry && worry.k === "tiny" && /third of an inch/.test(worry.says || ""),
            worry);
      check("and the button says what will happen, and that nothing is destroyed",
            worry && /nothing is cut again/.test(worry.tip || ""), worry && worry.tip);
      await page.val(`document.querySelector(".worries .waive").click(); true`);
      await sleep(1400);
      const waved = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const sp = waved.pieces.filter((p) => p.stem === "zz_speck")[0] || {};
      // ⭐️ ON THE PIECE, not in a list of its own, so it follows the piece
      // across a re-cut exactly as its name does
      check("saying it is fine is written on the piece itself",
            (sp.data || {}).fine === "tiny", sp.data);
      /* ⚠️ Read the row and the bar BEFORE touching the filters: pressing a
         filter chip shows whichever piece is first in the new list, so a
         check that pressed first would be reading a different piece. */
      const cleared = await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_speck"]');
        var out = { chip: r ? r.textContent.indexOf("very small") >= 0 : null,
                    said: !!document.querySelector(".worries .unwaive") };
        var f = document.querySelector('#pFilter button[data-f="odd"]');
        if (f) f.click();
        out.odd = !!document.querySelector('.prow[data-stem="zz_speck"]');
        var back = document.querySelector('#pFilter button[data-f=""]');
        if (back) back.click();
        return out; })()`);
      check("the flag goes from the row", cleared.chip === false, cleared);
      // ⭐️ THE POINT OF THE WHOLE THING: the list of things to deal with can
      // now be emptied, so it is worth opening
      check("and the piece drops out of Worth a look", cleared.odd === false, cleared);
      check("and the room says it was you who waved it through, and offers it back",
            cleared.said, cleared);
      // back onto the speck itself, which the filter chips will have left
      await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_speck"]');
        if (r) { r.scrollIntoView({ block: "center" }); r.click(); } return !!r; })()`);
      await sleep(700);
      await page.val(`document.querySelector(".worries .unwaive").click(); true`);
      await sleep(1400);
      const again = await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json();
      const sp2 = again.pieces.filter((p) => p.stem === "zz_speck")[0] || {};
      check("and flagging it again really does put it back",
            !((sp2.data || {}).fine || ""), sp2.data);
      fs.unlinkSync(speck);

      /* ⭐️ A CARD BACK SAYS SO, AND THEN IT IS THE ONLY THING IN THE LIST.
         The designer, 24 August 2026: "helpful if a card back element can be flagged
         as such, and then ONLY card backs appear in the ITS BACK dropdown, or
         that really is an exhaustive process." On a real game that list is two
         hundred pieces long and perhaps six of them are backs. */
      await fetch(`${ROOM}/api/p/${PROJECT}/manifest/zz_twin_b`, { method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind: "card back" }) });
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await page.val(`(function () {
        var r = document.querySelector('.prow[data-stem="zz_twin_a"]');
        if (r) { r.scrollIntoView({ block: "center" }); r.click(); } return !!r; })()`);
      await sleep(800);
      const backs = await page.val(`(function () {
        var s = document.getElementById("fBack");
        var only = document.getElementById("fBackOnly");
        function names() { return Array.prototype.map.call(s.options,
          function (o) { return o.value; }).filter(Boolean); }
        var narrow = names();
        only.checked = false; only.dispatchEvent(new Event("change"));
        var wide = names();
        return { narrow: narrow, wide: wide.length, ticked: true,
                 kinds: Array.prototype.map.call(
                   document.getElementById("fKind").options,
                   function (o) { return o.value; }) }; })()`);
      check("a piece can be marked as a card back",
            backs.kinds.indexOf("card back") >= 0, backs.kinds);
      check("and then it is the only thing offered as a back",
            backs.narrow.length === 1 && backs.narrow[0] === "zz_twin_b", backs.narrow);
      // ⚠️ it narrows; it never hides for good, or a back nobody had marked
      // could never be chosen at all
      check("with every piece still one tick away", backs.wide > backs.narrow.length,
            [backs.narrow.length, backs.wide]);

      /* ⚠️⚠️ A DROPDOWN BUILT ONCE GOES STALE, AND IT LOOKS LIKE A SHORTER
         LIST RATHER THAN AN OLD ONE. The designer, 24 August 2026: "I have marked 6
         different elements as card backs. When I do 'choose several at once'
         only one of those backs appears in the backs dropdown. It should
         contain the other card backs so I can batch add it (or I have to go
         through every card manually)."
         The bulk bar's list was rebuilt only when the NARROWING switched on
         or off, so it was built when one back existed and never again. Mark a
         second back with the bar open and both must be on it. */
      const oneBack = await page.val(`(function () {
        var only = document.getElementById("fBackOnly");
        if (only && !only.checked) { only.checked = true; only.dispatchEvent(new Event("change")); }
        var on = document.getElementById("pChooseOn");
        on.checked = true; on.dispatchEvent(new Event("change"));
        var s = document.getElementById("pChooseBack");
        var was = Array.prototype.map.call(s.options, function (o) { return o.value; }).filter(Boolean);
        var k = document.getElementById("fKind");
        k.value = "card back"; k.dispatchEvent(new Event("input"));
        return was; })()`);
      await sleep(1600);
      const twoBacks = await page.val(`(function () {
        var s = document.getElementById("pChooseBack");
        return Array.prototype.map.call(s.options, function (o) { return o.value; }).filter(Boolean); })()`);
      check("the bulk bar offers the back that was marked before it opened",
            oneBack.length === 1 && oneBack[0] === "zz_twin_b", oneBack);
      check("and a back marked while it is open joins it, instead of the list going stale",
            twoBacks.length === 2 && twoBacks.indexOf("zz_twin_a") >= 0, twoBacks);
      // put the bench back as it was: this piece is read again further down
      await page.val(`(function () {
        var k = document.getElementById("fKind");
        k.value = ""; k.dispatchEvent(new Event("input"));
        var on = document.getElementById("pChooseOn");
        on.checked = false; on.dispatchEvent(new Event("change")); return true; })()`);
      await sleep(1400);

      /* ⭐️⭐️ THE BOX BEING WORKED THROUGH COMES FIRST. The designer, 24 August 2026:
         "if I'm working with one supplement's elements, there doesn't seem to
         be a need to include all the possible choices for the core and the
         other boxes when I'm manually using the THIS IS THE COMPONENT dropdown?"

         Nothing says which SET a box of sheets answers to, so the room learns
         it from the links already made: link one piece off this book to a
         component in "core", and every other piece off that book is offered
         core's components first. */
      const list = await (await fetch(`${ROOM}/api/p/${PROJECT}/wanted`)).json();
      const core = (list.items || []).filter((w) => w.group === "core")[0];
      const offBook = (await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json())
        .pieces.filter((p) => p.sheet && bookish(p.sheet) === "proving-ground-sheets");
      /* ⚠️ NO SILENT SKIP. The first version of this check was wrapped in an
         `if` and the throwaway game turned out to have one piece off that book
         rather than two, so all three checks quietly did not happen and the
         run still came out green. A check that cannot run must SAY SO. */
      check("there is a component and a cut piece to try the banding on",
            !!core && offBook.length > 0,
            { core: !!core, pieces: offBook.length });
      if (core && offBook.length) {
        await fetch(`${ROOM}/api/p/${PROJECT}/manifest/${offBook[0].stem}`, { method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ wanted: core.id }) });
        await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
        await page.val(`(function () {
          var r = document.querySelector('.prow[data-stem="${offBook[0].stem}"]');
          if (r) { r.scrollIntoView({ block: "center" }); r.click(); } return !!r; })()`);
        await sleep(800);
        const bands = await page.val(`(function () {
          var s = document.getElementById("fWanted");
          return { bands: Array.prototype.map.call(s.querySelectorAll("optgroup"),
                     function (g) { return g.label; }),
                   all: Array.prototype.filter.call(s.options,
                     function (o) { return o.value; }).length }; })()`);
        const name = ((list.groups || []).filter((g) => g.id === "core")[0] || {}).name || "core";
        check("the components of the box this piece came out of come first",
              (bands.bands[0] || "").indexOf(name) === 0, bands.bands);
        // ⚠️ and the band is NAMED as though nothing came before it, because
        // nothing did: "the rest of core" at the top of the list reads as a
        // fault. This is what that check found the first time it was run.
        check("and it is not called the rest of something that is not there",
              (bands.bands[0] || "").indexOf("the rest of") !== 0, bands.bands);
        // ⚠️ IT ORDERS; IT DOES NOT HIDE. A piece cut from a supplement's
        // sheets may perfectly well be a core component that was reprinted.
        check("and every other component in the game is still on the list",
              bands.all === (list.items || []).length,
              [bands.all, (list.items || []).length]);
        check("each band saying how many it holds, so the length is no surprise",
              bands.bands.length > 1 && bands.bands.every((b) => /\(\d+\)$/.test(b)),
              bands.bands);
        /* ⭐️ AND THE CONTRAST, which is what shows the BOX is doing the work:
           a piece off no sheet the room knows belongs to no box, so there is
           nothing to put first and it gets the plain list back. */
        await page.val(`(function () {
          var r = document.querySelector('.prow[data-stem="zz_twin_a"]');
          if (r) { r.scrollIntoView({ block: "center" }); r.click(); } return !!r; })()`);
        await sleep(800);
        const loose = await page.val(`(function () {
          var s = document.getElementById("fWanted");
          return Array.prototype.map.call(s.querySelectorAll("optgroup"),
            function (g) { return g.label; }); })()`);
        check("while a piece off no known sheet has no box to put first",
              loose.length === 0 || !loose.some((b) => b.indexOf(name) === 0), loose);
        await fetch(`${ROOM}/api/p/${PROJECT}/manifest/${offBook[0].stem}`, { method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ wanted: "" }) });
      }

      /* ⭐️⭐️ THE CHECK AGAINST THE CONTENTS LIST, WHERE IT IS READ: on the
         way out, above the button, because it is the last thing to look at
         before the pieces leave the room.
         ⚠️ The panel gives COUNTS and opens the report; it does not say the
         findings again in its own words. Two accounts of the same findings
         would disagree within a fortnight (fault 24), so the check here is
         that the counts are there and that the report opens. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=export`);
      await sleep(1200);
      const onWayOut = await page.val(`(function () {
        var p = document.getElementById("reviewPanel");
        var sum = document.getElementById("reviewSum");
        var rights = document.getElementById("exportRights");
        return { there: !!p && p.offsetParent !== null,
                 says: sum ? sum.textContent.replace(/\\s+/g, " ").trim() : "",
                 items: sum ? sum.querySelectorAll("ul.found li").length : -1,
                 before: !!(p && rights &&
                   (p.compareDocumentPosition(rights) & Node.DOCUMENT_POSITION_FOLLOWING)),
                 button: !!document.getElementById("reviewOpen") }; })()`);
      check("the check against the list is on the way out, before the notice",
            onWayOut.there && onWayOut.before, onWayOut);
      check("and it says how the cut stands, in components and in pieces",
            /components accounted for/.test(onWayOut.says), onWayOut.says);
      check("with a line for each thing outstanding",
            onWayOut.items > 0, onWayOut.items);
      check("and a button to read the whole thing", onWayOut.button, onWayOut);
      const printed = await (await fetch(`${ROOM}/api/p/${PROJECT}/review/print`)).text();
      check("the report reads as a page, not as data",
            /<h1>/.test(printed) && /checked against the list/.test(printed),
            printed.slice(0, 60));

      twins.forEach(function (t) { fs.unlinkSync(t); });

      await page.go(`${ROOM}/p/${PROJECT}/?tab=match`);
      const mturn = await page.val(`(function () {
        var im = document.querySelector(".mcell .pic img");
        return im ? { t: im.style.transform, cls: im.className,
                      w: im.getBoundingClientRect().width,
                      h: im.getBoundingClientRect().height,
                      boxH: im.parentElement.getBoundingClientRect().height } : null; })()`);
      check("and so is its picture on the Match board",
            /rotate\(90deg\)/.test((mturn || {}).t || ""), mturn);
      // a quarter turn swaps width and height, so it must still fit the box
      check("a turned picture still fits inside its box",
            mturn && mturn.w <= mturn.boxH + 1, mturn);
      await page.shot("turned.png");
    }

    /* ⭐️⚠️ A ROOM RUNNING OLDER CODE THAN ITS PAGES MUST SAY SO. The designer, 23
       August 2026, pressing a button built that afternoon: "when I press
       'Split it' I get a 'no such call' error." The room had been open for
       hours; its pages are read off the disk every time, its Python is
       whatever was loaded when it started, and a running program cannot
       re-read itself. The button looked broken and the real trouble was
       silent. */
    {
      console.log("\ndoes a room running older code than its pages say so?");
      // ⚠️ asked from here, not from the page: an expression that hands back
      // a promise comes back as an empty object, which reads as an answer
      const clean = await (await fetch(`${ROOM}/api/health`)).json();
      check("a freshly opened room does not cry wolf", clean && clean.stale === false,
            clean);

      const src = "cutting_room.py";
      const was = fs.statSync(src);
      // ⚠️ exactly what an update does to it, and put back straight after so
      // that nothing else in this run — or in the working tree — is disturbed
      fs.utimesSync(src, new Date(), new Date());
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const bar = await page.val(`(function () { var b = document.getElementById("staleRoom");
        return b ? b.textContent : ""; })()`);
      check("a room whose code has changed under it says so, on the page",
            /running older code than these pages/.test(bar), bar.slice(0, 70));
      check("and says what to do about it", /Close the room and open it again/.test(bar));
      check("and that nothing is at risk", /on the disk/.test(bar));

      fs.utimesSync(src, was.atime, was.mtime);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      check("and it is quiet again once the room is the code it started from",
            !(await page.val(`!!document.getElementById("staleRoom")`)));
    }

    // ---------------------------------------------------- the offline page
    if (BAKED) {
      console.log("\nthe same editor, baked and opened from a file");
      thrown.length = 0;
      await page.go("file://" + BAKED);
      const o = await page.val(SHAPE);
      check("the offline page is no wider than the window", o.pageW <= o.innerW + 1,
            { pageW: o.pageW, stretchedBy: o.tooWide });
      check("its canvas is stage-sized too", o.canvasW < o.innerW, [o.canvasW, o.canvasH]);
      check("its sheet is drawn out of the page's own data", o.inked > 0, o.inked);
      check("it has no room fittings on it",
            (await page.val(`!document.getElementById("roomCut")`)) === true);
      await page.shot("baked.png");
    }

    check("nothing was thrown along the way", thrown.length === 0, thrown.slice(0, 3));
  } finally {
    try { await page.send("Browser.close"); } catch (e) { /* going anyway */ }
    chrome.kill("SIGKILL");
    fs.rmSync(profile, { recursive: true, force: true });
  }

  const wrong = done.filter((d) => !d.right);
  console.log(wrong.length
    ? `\n${wrong.length} of ${done.length} checks are WRONG`
    : `\nall ${done.length} checks came out right`);
  process.exit(wrong.length ? 1 : 0);
})().catch((e) => { console.error("\nthe check itself broke: " + e.message); process.exit(2); });
