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
    /* ⭐️ TWO ACTIONS ON ONE KEY EACH. The designer, 25 August 2026: "is there
       (or can there be) a shortcut for duplicate piece please - needs to be a
       button that won't trigger anything else though (maybe the + = key?)",
       and then "also a shortcut to delete the selected piece (x maybe?)".
       ⚠️ The "won't trigger anything else" half is the half worth checking, so
       it is checked first: both keys pressed with the pointer in a text box
       must do nothing but type (fault 2). The note box is used for it, and
       emptied again, so nothing is left behind for the checks after this. */
    await page.val(`document.getElementById("pieceNote").focus(); true`);
    await page.press("+");
    await page.press("x");
    await sleep(300);
    const inBox = await page.val(`(function () {
      var n = document.getElementById("pieceNote");
      var was = { typed: n.value, pieces: document.querySelectorAll("#pieces .piece").length };
      n.value = "";
      n.dispatchEvent(new Event("input", { bubbles: true }));
      n.blur();
      return was; })()`);
    check("the duplicate and delete keys do not fire while you are typing",
          inBox && inBox.pieces === 1 && inBox.typed === "+x", inBox);
    await sleep(400);

    await page.press("+");
    await sleep(500);
    const twinned = await page.val(`(function () {
      var rows = document.querySelectorAll("#pieces .piece");
      var adj = document.getElementById("tAdjust");
      return { n: rows.length,
               tool: adj ? adj.getAttribute("aria-pressed") : "" }; })()`);
    check("the + key lays another copy of the chosen piece down",
          twinned && twinned.n === 2, twinned);
    // ⭐️ the copy arrives ready to be dragged where it belongs, which is the
    // whole point of duplicating rather than drawing it again
    check("and hands it to Adjust, ready to be dragged into place",
          twinned && twinned.tool === "true", twinned);
    /* ⭐️ AND THE THIRD KEY OF THE SAME ASK: "another shortcut for work on
       this piece alone". With two pieces on the sheet it can be seen doing
       something — one row dimmed in the rail, the other outline off the
       picture. ⚠️ It is a TOGGLE, because a key that could only switch the
       hiding ON would leave a state nothing could clear (fault 50). */
    await page.press("o");
    await sleep(500);
    const only = await page.val(`(function () {
      var rows = document.querySelectorAll("#pieces .piece");
      return { hidden: document.querySelectorAll("#pieces .piece.hidden").length,
               rows: rows.length,
               ticked: document.getElementById("soloPiece").checked,
               said: document.getElementById("hint").textContent }; })()`);
    check("the O key works on the chosen piece alone, hiding the others",
          only && only.hidden === 1 && only.ticked, only);
    // ⚠️⚠️ On a sheet of forty counters this takes thirty-nine outlines off
    // the picture at a stroke. It must say that nothing was deleted.
    check("saying they are hidden and not deleted, and how to bring them back",
          only && /hidden, not deleted/.test(only.said || "")
          && only.rows === 2, only && only.said);
    await page.press("o");
    await sleep(500);
    const backAgain = await page.val(`(function () { return {
      hidden: document.querySelectorAll("#pieces .piece.hidden").length,
      ticked: document.getElementById("soloPiece").checked }; })()`);
    check("and the same key brings them back, the tick box following it",
          backAgain && backAgain.hidden === 0 && backAgain.ticked === false, backAgain);

    await page.press("x");
    await sleep(500);
    const gone = await page.val(`(function () {
      return { n: document.querySelectorAll("#pieces .piece").length,
               said: document.getElementById("hint").textContent,
               name: (document.querySelector("#pieces .piece .nm") || {}).textContent }; })()`);
    check("and the X key takes the chosen piece off the sheet again",
          gone && gone.n === 1, gone);
    // ⚠️⚠️ A DESTRUCTIVE THING ON ONE KEY MUST SAY HOW TO UNDO IT. The button
    // is a deliberate press with a sentence on it; X is one finger.
    check("saying in the same breath how to put it back",
          gone && /puts it back/.test(gone.said || ""), gone && gone.said);
    check("and it took the copy, leaving the named original where it was",
          gone && gone.name === NAME, gone && gone.name);

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

    /* ⭐️⭐️ THE AUTOMATIC FIRST ATTEMPT, PRESSED RATHER THAN ASKED FOR. The
       designer, 25 August 2026: "the auto cutting pass is essentially
       pointless" — every outline it offered arrived at the editor as a CURVE,
       so a four-cornered counter was drawn as a Bézier through its corners
       and came out bowed. The shapes themselves are checked in
       check/the_automatic_pass.py; what is checked HERE is the wire between
       them, which is where it was broken: the room says straight or curved
       and the editor has to believe it. Fault 61 — a check through the API is
       a green light over a button that does nothing. */
    if (OUTLINES) {
      console.log("\nthe automatic attempt at a sheet, from the button");
      await page.val(`document.querySelectorAll(".tab")[20].click(); true`);
      await sleep(1400);
      await page.val(`(function () { var b = document.getElementById("suggest");
        if (b) b.click(); return !!b; })()`);
      // the room works the sheet out the first time it is asked, so the press
      // may have to be made again once the answer has arrived
      for (let i = 0; i < 40; i++) {
        const n = await page.val(`document.querySelectorAll("#pieces .piece").length`);
        if (n > 0) break;
        await page.val(`(function () { var b = document.getElementById("suggest");
          if (b && !b.disabled) b.click(); return true; })()`);
        await sleep(500);
      }
      const drew = await page.val(`(function () { return {
        rows: document.querySelectorAll("#pieces .piece").length }; })()`);
      check("pressing it outlines the pieces the room can find", drew.rows >= 3, drew);
      await sleep(1800);
      const book2 = JSON.parse(fs.readFileSync(OUTLINES, "utf8"));
      const made = ((book2.sheets || {})["proving-ground-sheets-21"] || {}).pieces || [];
      check("and the outlines reach the project's own file", made.length >= 3,
            made.length);
      /* ⚠️ THE ONE THAT MATTERS. A counter is not a coastline: a shape the
         room fitted as a rectangle must arrive as four STRAIGHT nodes, or the
         editor bends its sides and the person redraws it by hand. */
      const flat = made.filter((p) => p.curve === false);
      check("a shape the room fitted as a rectangle stays straight-sided",
            flat.length >= 1 && flat.every((p) => (p.pts || []).length === 4),
            made.map((p) => [(p.pts || []).length, p.curve]));
      check("and the traced ones are still curves, with a handful of nodes",
            made.some((p) => p.curve === true) &&
            made.every((p) => (p.pts || []).length <= 60),
            made.map((p) => (p.pts || []).length));
      await page.val(`document.querySelectorAll(".tab")[0].click(); true`);
      await sleep(1000);
    }

    /* ⭐️⭐️ MASKING OFF A PART OF A SHEET. The designer, 25 August 2026: "one
       quick tool that would be useful would be the ability to mask off a
       section of any given sheet, so that it doesn't get run for
       suggestions." What the room does with a region is checked through the
       API in check.sh; what is checked HERE is the wire — that dragging a box
       on the sheet really reaches the room's own file. Fault 61: a check
       through the API is a green light over a button that does nothing. */
    if (BED) {
      console.log("\nmasking off a part of a sheet");
      const MSID = "proving-ground-sheets-35";
      const meta = () => JSON.parse(fs.readFileSync(path.join(BED, "project.json"), "utf8"))
        .sheets.filter((x) => x.id === MSID)[0] || {};
      await page.val(`document.querySelectorAll(".tab")[34].click(); true`);
      await sleep(1200);
      const tool = await page.val(`(function () {
        var b = document.getElementById("tSkip");
        return { has: !!b, seen: !!b && b.offsetWidth > 0,
                 sheet: document.querySelector(".tab.on") ?
                        document.querySelector(".tab.on").textContent : "" }; })()`);
      check("the table the room serves offers a Mask off tool",
            tool && tool.has && tool.seen, tool);
      const box = await page.val(`(function(){ var r = document.getElementById("cv").getBoundingClientRect();
        return { x: r.x, y: r.y, w: r.width, h: r.height }; })()`);
      await page.press("m");
      const armed = await page.val(`document.getElementById("tSkip").getAttribute("aria-pressed")`);
      check("and the M key puts it in hand", armed === "true", armed);
      const m1 = { x: box.x + box.w * 0.30, y: box.y + box.h * 0.28 };
      const m2 = { x: box.x + box.w * 0.62, y: box.y + box.h * 0.55 };
      await page.mouse("mousePressed", m1.x, m1.y, 1);
      for (let i = 1; i <= 10; i++) {
        await page.mouse("mouseMoved", m1.x + (m2.x - m1.x) * i / 10,
                         m1.y + (m2.y - m1.y) * i / 10, 1);
      }
      await page.mouse("mouseReleased", m2.x, m2.y, 0);
      await sleep(900);
      const wrote = meta();
      check("a box dragged over the sheet reaches the room's own file",
            (wrote.skip || []).length === 1, wrote.skip);
      // ⚠️ and it says what it did, because a mask is a thing you must be
      // able to see you did — a sheet that comes back with nothing suggested
      // on half of it otherwise reads as a fault in the room
      const said = await page.val(`document.getElementById("hint").textContent`);
      check("and the table says nothing was deleted and how to take it off",
            /Masked off/.test(said || "") && /nothing is deleted/.test(said || ""), said);
      /* ⚠️ A REGION NOTHING CAN CLEAR IS FAULT 50's SHAPE. It hides part of
         the sheet from the automatic pass, so taking one off has to be as
         easy as putting it on. */
      const mid = { x: (m1.x + m2.x) / 2, y: (m1.y + m2.y) / 2 };
      await page.mouse("mousePressed", mid.x, mid.y, 1);
      await page.mouse("mouseReleased", mid.x, mid.y, 0);
      await sleep(900);
      check("and clicking the box takes it off again, in the room too",
            (meta().skip || []).length === 0, meta().skip);
      await page.press("t");
      await page.val(`document.querySelectorAll(".tab")[0].click(); true`);
      await sleep(800);
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

      /* ⭐️ HELD BACK IS A LIST TO COME BACK TO, SO IT HAS TO BE GETTABLE AT.
         A piece can be marked *hold back* with a reason — the artwork wants
         redoing, the rules are unclear — and it stays in the folder with
         everything else. Until this chip the only way to find the four pieces
         somebody had put off was to open all two hundred one at a time, or to
         print the whole report. And the reason goes on the ROW: a list of six
         pieces that all say nothing but "held back" is a list you still have
         to open six times. */
      const holdable = (await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json())
        .pieces.filter((p) => p.stem.indexOf("zz_") !== 0 && !(p.data || {}).spare);
      const heldA = (holdable[0] || {}).stem;
      // ⚠️ its own piece, not the second one that happens to be lying about:
      // written that way there WAS no second one, so the stem came out
      // `undefined`, the room dutifully wrote a manifest entry under that
      // name, and the check went red pointing at the page rather than at
      // itself. A bench that borrows whatever it finds is a bench that breaks
      // when the run before it changes.
      const heldB = "zz_held";
      fs.copyFileSync(process.env.COUNTER, path.join(BED, "pieces", heldB + ".png"));
      const hold = (stem, why) =>
        fetch(`${ROOM}/api/p/${PROJECT}/manifest/${stem}`, { method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ hold: why }) });
      const putAside = (stem, aside) =>
        fetch(`${ROOM}/api/p/${PROJECT}/pieces/aside`, { method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stems: [stem], aside }) });
      await hold(heldA, "artwork");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await sleep(800);
      const onHold = await page.val(`(function () {
        var f = document.querySelector('#pFilter button[data-f="held"]');
        if (!f) return null;
        f.click();
        var rows = document.querySelectorAll("#plist .prow");
        return { n: rows.length, stem: rows[0] ? rows[0].dataset.stem : "",
                 says: rows[0] ? rows[0].textContent : "" }; })()`);
      check("the pieces being held back can be listed on their own",
            onHold && onHold.n === 1 && onHold.stem === heldA, onHold);
      check("and the row says why that one is being held",
            onHold && /held back: artwork/.test(onHold.says || ""), onHold && onHold.says);

      /* ⚠️ A PIECE SET ASIDE AND ALSO HELD BACK IS ON THIS LIST, DIMMED, because
         every chip on this page shows what is set aside rather than hiding it —
         a filter that quietly drops rows is how the room loses things (fault
         44). The printed check against the contents list counts the other way:
         a piece set aside is counted as set aside and nothing else. So the two
         numbers really do differ, and the list SAYS what the difference is made
         of rather than letting them disagree in silence. */
      await hold(heldB, "wrong scan");
      await putAside(heldB, true);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await sleep(800);
      const mixed = await page.val(`(function () {
        document.querySelector('#pFilter button[data-f="held"]').click();
        var put = document.querySelector('#plist .prow[data-stem="${heldB}"]');
        return { n: document.querySelectorAll("#plist .prow").length,
                 dim: !!put && /aside/.test(put.className),
                 count: document.getElementById("pCount").textContent }; })()`);
      check("a piece set aside is still on the held-back list, dimmed, not hidden from it",
            mixed && mixed.n === 2 && mixed.dim, mixed);
      check("and the list says how many of it are set aside, which is what the printed check leaves out",
            mixed && /1 set aside/.test(mixed.count || ""), mixed && mixed.count);

      /* ⭐️ AND THE REPORT'S COUNT IS A WAY IN TO THE PIECES IT COUNTS. "1 piece
         held back" was a number with no route to the piece — you opened pieces
         one at a time until you found it, or printed the whole check. */
      await page.go(`${ROOM}/p/${PROJECT}/?tab=export`);
      await sleep(1800);
      const rep = await page.val(`(function () {
        var a = document.querySelector('#reviewSum a[data-chip="held"]');
        return { has: !!a, says: a ? a.textContent : "",
                 all: document.getElementById("reviewSum").textContent }; })()`);
      check("the end-of-job report's count of pieces held back is a link into that list",
            rep && rep.has && /^1 piece held back$/.test((rep.says || "").trim()), rep);
      /* ⚠️ `if (a)`, not a bare click: with the link gone this threw inside the
         page, the throw ended the WHOLE browser section — some eighty checks
         after it never ran, and the bench kept the piece this block makes,
         which turned four more checks red for reasons that were nothing to do
         with them. A check that crashes reports one fault as six. */
      await page.val(`(function () {
        var a = document.querySelector('#reviewSum a[data-chip="held"]');
        if (a) a.click(); return !!a; })()`);
      await sleep(1400);
      const landed = await page.val(`(function () {
        return { tab: !document.getElementById("tab-pieces").hidden,
                 on: !!document.querySelector('#pFilter button[data-f="held"].on'),
                 n: document.querySelectorAll("#plist .prow").length }; })()`);
      check("and pressing it opens the Pieces page with that chip already chosen",
            landed && landed.tab && landed.on && landed.n === 2, landed);

      /* ⚠️ AND THE OTHER HALF OF IT: nothing held back is the GOOD answer, and
         a blank page reads as a broken screen rather than as good news. */
      await hold(heldA, "");
      await hold(heldB, "");
      await putAside(heldB, false);
      fs.unlinkSync(path.join(BED, "pieces", heldB + ".png"));
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces`);
      await sleep(800);
      const clear = await page.val(`(function () {
        var f = document.querySelector('#pFilter button[data-f="held"]');
        f.click();
        return { n: document.querySelectorAll("#plist .prow").length,
                 note: (document.querySelector("#plist .note") || {}).textContent || "" }; })()`);
      check("letting a piece go empties that list again", clear && clear.n === 0, clear);
      check("and the empty list says which empty it is",
            clear && /Nothing is being held back/.test(clear.note || ""), clear);

      /* ⭐️⭐️ AND THE OTHER WAY IN: ?piece=<stem> OPENS ONE PIECE BY NAME.
         The end-of-job check names pieces by their stem and could not open
         one, so every finding was a name to go and hunt for through two
         hundred rows. The report the room serves links each stem here.
         ⚠️ Pick the LAST piece, not the first: the list opens on the first
         thing it can find, so landing on that would be a check that passes
         whether or not the address was read at all. */
      const everyPiece = (await (await fetch(`${ROOM}/api/p/${PROJECT}/pieces`)).json()).pieces;
      const target = (everyPiece[everyPiece.length - 1] || {}).stem;
      await page.go(`${ROOM}/p/${PROJECT}/?tab=pieces&piece=${target}`);
      await sleep(1200);
      const gotThere = await page.val(`(function () {
        var on = document.querySelector("#plist .prow.on");
        return { tab: !document.getElementById("tab-pieces").hidden,
                 on: on ? on.dataset.stem : "",
                 addr: location.search + location.hash }; })()`);
      check("a link naming one piece opens the Pieces page on that piece",
            gotThere && gotThere.tab && gotThere.on === target, gotThere);
      /* ⚠️ AND IT ACTS ONCE. Left sitting in the address, every later hash
         change — pressing Pieces again after a look at Match — would drag you
         back to the same piece: a link that will not let go. */
      check("and the piece is taken out of the address, so it does not keep pulling you back",
            gotThere && !/piece=/.test(gotThere.addr || ""), gotThere && gotThere.addr);

      /* ⚠️⚠️ THE HALF THAT MATTERS: A LINK MUST NEVER LAND ON A HIDDEN ROW.
         This list is held to a chip and to a box for as long as the page is
         open, so a piece asked for while a chip is on can be sitting behind a
         narrowing chosen twenty minutes ago — and the press would appear to do
         nothing at all. Fault 44's shape: the one thing asked for is the one
         thing hidden. Nothing is held back by now, so that chip shows an empty
         list, which is the worst case there is. */
      const behind = await page.val(`(function () {
        document.querySelector('#pFilter button[data-f="held"]').click();
        var hidden = document.querySelectorAll("#plist .prow").length;
        location.hash = "pieces//${target}";
        return hidden; })()`);
      await sleep(900);
      const dug = await page.val(`(function () {
        var on = document.querySelector("#plist .prow.on");
        return { on: on ? on.dataset.stem : "",
                 chip: !!document.querySelector('#pFilter button[data-f="held"].on'),
                 n: document.querySelectorAll("#plist .prow").length }; })()`);
      check("a piece behind a narrowing that hides it is still opened, and the narrowing cleared",
            behind === 0 && dug && dug.on === target && !dug.chip && dug.n > 1,
            [behind, dug]);

      /* ⚠️ AND A PIECE THAT IS NOT THERE SAYS SO. Quietly showing the first
         piece in the list instead would look for all the world as though the
         link had worked, which is fault 58's lesson: half working is worse
         than not working. */
      await page.val(`(function () { location.hash = "pieces//no-such-piece-at-all"; })()`);
      await sleep(900);
      const nope = await page.val(`(function () {
        var on = document.querySelector("#plist .prow.on");
        return { said: document.getElementById("flash").textContent,
                 on: on ? on.dataset.stem : "" }; })()`);
      check("and a piece the room has not got says so rather than opening another one",
            nope && /no piece called no-such-piece-at-all/.test(nope.said || "")
            && nope.on === target, nope);

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
      check("and says what to do about it", /Start it again/.test(bar));
      check("and that nothing is at risk", /on the disk/.test(bar));
      /* ⭐️ AND THE BUTTON IS IN THE BANNER. The designer, 24 August 2026: "is there a
         way to build a relaunch button into the browser tab it uses somehow?"
         This banner is the one place in the room where somebody has just been
         told to do something that meant finding a Terminal window.
         ⚠️ It is read, NOT pressed: pressing it here would restart the room
         out from under every check that comes after this one. */
      // ⚠️ `title` OR `data-tip`: tips.js takes a plain title over as its own
      // bubble and takes the attribute off, so reading .title alone finds
      // nothing and calls a well-explained button unexplained (fault 31).
      const button = await page.val(`(function () {
        var b = document.querySelector("#staleRoom button");
        return b ? { says: b.textContent,
                     tip: b.title || b.getAttribute("data-tip") || "" } : null; })()`);
      check("and offers the button that does it, in the banner itself",
            button && /Start the room again/.test(button.says || ""), button);
      check("which says what will happen and that the page comes back",
            button && /same window/.test(button.tip || "") &&
            /comes back/.test(button.tip || ""), button && button.tip);
      check("and the same offer sits in the bar at the top of every page",
            await page.val(`(function () { var a = document.getElementById("againRoom");
              return !!a && /Start it again/.test(a.textContent) &&
                     !!(a.title || a.getAttribute("data-tip")); })()`));

      fs.utimesSync(src, was.atime, was.mtime);
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      check("and it is quiet again once the room is the code it started from",
            !(await page.val(`!!document.getElementById("staleRoom")`)));
    }

    /* ⭐️⭐️ SOMETHING TO WATCH WHILE A LINK IS FETCHED. The designer, 24 August
       2026: "I'm trialling importing a google doc - have pasted the open link,
       and pressed Fetch - status says 'Fetching...' but would be much more
       useful if that were an actual progress bar or at the very least
       something a little more animated so i can see if it's stalled."
       A frozen word cannot answer the one question anybody asks during a
       wait. The room reads the file in pieces and counts them, so there is a
       bar that fills, a size that keeps moving, and a clock.
       ⚠️ Its own project, so a sheet arriving from a link cannot change the
       sheet counts every other check in here is reading. */
    if (process.env.SLOW_URL) {
      console.log("\nfetching a file from a link, with something to watch");
      const made = await (await fetch(`${ROOM}/api/projects`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "A Slow Link" }) })).json();
      const pid = made.project && made.project.id;
      await page.go(`${ROOM}/p/${pid}/?tab=sheets`);
      await page.val(`(function () {
        var d = document.querySelector("details.linkdetail");
        if (d) d.open = true;
        document.getElementById("fetchUrl").value = ${JSON.stringify(process.env.SLOW_URL)};
        document.getElementById("fetchGo").click(); return true; })()`);
      let sawBar = false, sawFill = false, sawBytes = false, sawClock = false, over = false;
      for (let i = 0; i < 90 && !over; i++) {
        const st = await page.val(`(function () {
          var b = document.getElementById("progbar");
          var p = document.getElementById("progress");
          return { on: !!b && !b.hidden,
                   w: b ? b.querySelector("i").style.width : "",
                   says: p ? p.textContent : "" }; })()`);
        if (st.on) sawBar = true;
        if (/%$/.test(st.w) && parseFloat(st.w) > 0) sawFill = true;
        if (/downloading/.test(st.says)) sawBytes = true;
        if (/·\s*\d+s/.test(st.says)) sawClock = true;
        if (/sheets? added/.test(st.says) || /^⚠/.test(st.says)) over = true;
        await sleep(200);
      }
      check("a link being fetched puts up a bar to watch", sawBar);
      // ⚠️ the bar FILLING is the half that says how far along it is; a bar
      // that only ever creeps says no more than the word "Fetching…" did
      check("and the bar fills as the bytes come down, not merely creeps", sawFill);
      check("and the room says how much has arrived", sawBytes);
      check("and how long it has been going, so a slow link is not a dead one", sawClock);
      const after = await (await fetch(`${ROOM}/api/p/${pid}`)).json();
      check("and what was at the end of the link becomes a sheet",
            (after.sheets || []).length === 1, (after.sheets || []).length);
      check("with the bar taken down again when it is over",
            await page.val(`document.getElementById("progbar").hidden === true`));
      await page.shot("fetching.png");
    }

    /* ⚠️⚠️ A BUTTON THAT READS A CONTROL THAT IS NOT THERE DOES NOTHING AT
       ALL, AND SAYS NOTHING EITHER. The designer, 25 August 2026: "I have the contents
       list for the core box, pasted it into the checklist field, but the
       'Add them' button doesn't seem to do anything."
       It read a tick box that had never been in the page, threw, and stopped
       — with the list sitting there, apparently ignored. Every check the room
       had went through the API, which worked perfectly. This one presses the
       button.
       ⭐️ And the other half of the same message: "how do I add a separate
       contents list for core as opposed to [the supplement]?" — a set can be
       made from the panel itself now, so one box's list goes in at a time. */
    {
      console.log("\npasting a contents list in, one box at a time");
      const born = await (await fetch(`${ROOM}/api/projects`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "A Pasted List" }) })).json();
      const pid = born.project && born.project.id;
      await page.go(`${ROOM}/p/${pid}/?tab=wanted`);
      const panel = await page.val(`(function () {
        window.prompt = function () { return "Terror in the Dark"; };
        document.getElementById("wStart").click();
        return { open: !document.getElementById("wImport").hidden,
                 tick: !!document.getElementById("wImportEach"),
                 sets: Array.prototype.map.call(
                   document.getElementById("wImportGroup").options,
                   function (o) { return o.value; }) }; })()`);
      check("the panel that takes a pasted list is there when the list is empty",
            panel.open, panel);
      // ⚠️ THE FAULT ITSELF: this control was read by the button and had never
      // existed in the page
      check("and the tick that says whether these are all different is really in it",
            panel.tick, panel);
      check("and a set can be made from the panel, so one box goes in at a time",
            (panel.sets || []).indexOf("__new") >= 0, panel.sets);
      await page.val(`(function () {
        /* ⚠️ FAULT 27 AGAIN: inside a template literal a backslash escape is
           eaten before the expression is ever sent, so a "\n" written here
           arrives as a real newline, ends the string it is in, and the page
           throws a SyntaxError. Built out of a list instead, which has no
           escape in it to lose. */
        document.getElementById("wText").value =
          ["26 Damage counters", "12 Doors", "2 Boards"].join(String.fromCharCode(10));
        document.getElementById("wImportGroup").value = "__new";
        document.getElementById("wImportGo").click(); return true; })()`);
      await sleep(1800);
      const landed = await page.val(`(function () {
        return { rows: document.querySelectorAll("#wBody tr.missing, #wBody tr.cut, #wBody tr.part, #wBody tr.probably").length,
                 heads: Array.prototype.map.call(document.querySelectorAll("#wBody .fold .what"),
                   function (h) { return h.textContent; }),
                 said: (document.querySelector(".flash") || {}).textContent || "" }; })()`);
      check("pressing Add them puts every line on the checklist",
            landed.rows === 3, landed);
      check("and says how many it added, rather than nothing at all",
            /3 components added/.test(landed.said || ""), landed.said);
      check("under the set it was told to make, by the name it was given",
            (landed.heads || []).indexOf("Terror in the Dark") >= 0, landed.heads);
      // ⚠️ and the set's NAME reaches the disk, or the next load shows a bare id
      const kept = await (await fetch(`${ROOM}/api/p/${pid}/wanted`)).json();
      check("and the new set is written down, name and all",
            (kept.groups || []).some((g) => g.name === "Terror in the Dark"),
            kept.groups);
      check("with every component in it", (kept.items || []).length === 3,
            (kept.items || []).length);
    }

    /* ⭐️⭐️ A SET TAKES ITS NAME FROM THE BOX IT BELONGS TO. The designer, 25
       August 2026: "the +add a new box should surely take its cue from the
       headings I've provided in #import? Otherwise how will it
       differentiate?" By then they had named the boxes their scans came in
       as, and the room was asking them to type those names a second time and
       hoping the two matched. */
    {
      console.log("\na set of components takes its name from a box of sheets");
      await fetch(`${ROOM}/api/p/the-spare-room/book/keepers`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "The Keepers Box" }) });
      await page.go(`${ROOM}/p/the-spare-room/?tab=wanted`);
      const offered = await page.val(`(function () {
        document.getElementById("wStart").click();
        var sel = document.getElementById("wImportGroup");
        return Array.prototype.map.call(sel.options, function (o) {
          return o.value + " = " + o.textContent; }); })()`);
      check("the boxes of sheets in this game are offered as sets, by the names given them",
            offered.some((o) => /^__book:keepers = The Keepers Box/.test(o)), offered);
      await page.val(`(function () {
        document.getElementById("wText").value =
          ["8 Skeletons", "2 Doors"].join(String.fromCharCode(10));
        document.getElementById("wImportGroup").value = "__book:keepers";
        document.getElementById("wImportGo").click(); return true; })()`);
      await sleep(1800);
      const book = await (await fetch(`${ROOM}/api/p/the-spare-room/wanted`)).json();
      const set = (book.groups || []).filter((g) => g.name === "The Keepers Box")[0];
      check("picking one makes a set of that name, without anybody typing it again",
            !!set, book.groups);
      /* ⭐️ and it SAYS which box it answers to, which is the question the room
         otherwise has to infer from the links already made (fault 51) — right
         from the first component, before any piece has been linked at all. */
      check("and the set knows which box of sheets it belongs to",
            set && set.book === "keepers", set);
      check("with the pasted components in it",
            (book.items || []).filter((i) => i.group === (set || {}).id).length === 2,
            (book.items || []).length);
    }

    /* ⭐️⭐️ WHAT IS BEING CUT NOW, AND WHAT WAS ONLY UPLOADED FOR LATER. The
       designer, 25 August 2026: "I find the overall checklist % isn't very
       helpful... I've decided to not yet cut some pieces which belong to
       advanced rule sets that I don't want to bring in the v1 of the game.
       Maybe I need a user-defined divide between live cutting and a sheet
       backlog/future cutting which I may have uploaded only for convenience?"
       ⚠️ The API is checked elsewhere; this is the half that goes wrong
       unwatched — fault 61's lesson, that a check going through the API is a
       green light over a button that does nothing. */
    /* ⚠️⚠️ THE BUTTON THAT CUTS A RUN OF SHEETS SAYS WHAT IT WILL DO.
       The designer, 26 August 2026: "I think pressed 'cut every outlined
       sheet', next to which it said '22 not cut yet'. But it then started
       cutting every single page I have ever outlined in the entire game."
       The words and the action were worked out separately and disagreed, so
       what has to be checked is that the button's own face now names the
       number the room will act on — and that narrowing the list changes it.
       ⚠️ The API is checked elsewhere; this is fault 61's half, where a
       green light over a button that does nothing gets written. */
    {
      console.log("\nthe button that cuts a run of sheets says what it will do");
      // put fresh outlines on the two newbox sheets, so they are waiting
      // again while oldbox-01 stays cut and untouched
      for (const sid of ["newbox-01", "newbox-02"]) {
        await fetch(`${ROOM}/api/p/the-cutting-queue/outlines/${sid}`,
          { method: "PUT", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pieces: [
              { pts: [[200, 200], [700, 200], [700, 700], [200, 700]] },
              { pts: [[900, 900], [1400, 900], [1400, 1400], [900, 1400]] }] }) });
      }
      await page.go(`${ROOM}/p/the-cutting-queue/?tab=sheets`);
      await sleep(500);
      const all = await page.val(`(function () {
        var a = document.querySelector('#sFilter button[data-f=""]');
        if (a) a.click();
        return true; })()`);
      await sleep(500);
      const face = await page.val(`(function () { return {
        says: (document.getElementById("cutAll") || {}).textContent || "",
        note: (document.getElementById("cutAllNote") || {}).textContent || "",
        cards: document.querySelectorAll(".sheets .sheet").length }; })()`);
      check("the button names the number of sheets it will cut, not the whole game",
            /Cut the 2 sheets waiting here/.test(face.says), face.says);
      // ⚠️ AND IT SAYS WHAT IT IS SKIPPING. The sheet already cut is the
      // whole complaint; a button that silently left it out would be as hard
      // to trust as one that silently cut it again.
      check("and it says the sheet already cut is being skipped",
            /1 already cut sheet is skipped/.test(face.note), face.note);

      /* ⭐️ "OR JUST CUT THE ONES I'M LOOKING AT WITHIN THE CURRENT IMPORT."
         The list is already held to a box, a search and a filter, so the
         narrowing they have made IS the answer — and the number on the
         button has to follow it. */
      await page.val(`(function () { var f = document.getElementById("sFind");
        f.value = "newbox-01"; f.dispatchEvent(new Event("input", {bubbles:true}));
        return true; })()`);
      await sleep(500);
      const narrowed = await page.val(`(function () { return {
        says: (document.getElementById("cutAll") || {}).textContent || "",
        note: (document.getElementById("cutAllNote") || {}).textContent || "" }; })()`);
      check("narrowing the list to one sheet narrows the button to one sheet",
            /Cut the 1 sheet waiting here/.test(narrowed.says), narrowed.says);
      // ⚠️ AND A NARROWING IS NEVER SILENT: a button quietly doing less than
      // you think is the whole of what went wrong here.
      check("and it says how many are waiting that this list is not showing",
            /1 more sheet is waiting but not shown/.test(narrowed.note), narrowed.note);

      // ⭐️ and pressing it really cuts THAT sheet and leaves the other waiting
      await page.val(`(function () { document.getElementById("cutAll").click(); return true; })()`);
      await sleep(6000);
      const after = await fetch(`${ROOM}/api/p/the-cutting-queue`).then(r => r.json());
      const state = {};
      after.sheets.forEach(function (x) { state[x.id] = [x.cut, !!x.stale]; });
      check("pressing it cuts the sheet it named and leaves the other waiting",
            state["newbox-01"] && state["newbox-01"][1] === false &&
            state["newbox-02"] && state["newbox-02"][1] === true, state);
      // put the search back, so nothing after this looks at a narrowed list
      await page.val(`(function () { var f = document.getElementById("sFind");
        f.value = ""; f.dispatchEvent(new Event("input", {bubbles:true}));
        return true; })()`);
      await sleep(300);
    }

    /* ⚠️⚠️ A DECK STAYS ON THE MATCH LIST UNTIL IT HAS ENOUGH CARDS, AND
       CARRIES A ROW FOR ITS BACK. The designer, 26 August 2026: "if I mark one
       magic card as part of a deck, that then disappears from the left column,
       even though I might have numerous more cards to mark as part of that
       deck. The only way to get it back is to click 'show everything,
       including matched' which isn't a great experience… ALSO match should
       include an item for the relevant back of each deck."
       ⚠️ The rules are checked through the API elsewhere; this is the half
       that goes wrong unwatched — fault 61, a green light over a list that
       still empties itself. */
    {
      console.log("\na deck on the Match board, and the row for its back");
      const QUEUE = "the-cutting-queue";
      const wl = await fetch(`${ROOM}/api/p/${QUEUE}/wanted`).then(r => r.json());
      const deck = (wl.items || []).filter(i => i.name === "Magic cards")[0] || {};
      // start from a deck with no back said, so the row to drag is there
      await fetch(`${ROOM}/api/p/${QUEUE}/wanted/back`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: deck.id, stem: "" }) });
      await page.go(`${ROOM}/p/${QUEUE}/?tab=match`);
      await sleep(900);
      const seen = await page.val(`(function () {
        var rows = document.querySelectorAll("#mList .mitem");
        var out = { deck: null, back: null, all: !!document.getElementById("mAll").checked };
        rows.forEach(function (r) {
          if (r.dataset.id) { var b = r.querySelector("b");
            if (b && b.textContent === "Magic cards")
              out.deck = (r.querySelector(".tag") || {}).textContent || ""; }
          if (r.dataset.back) out.back = r.textContent; });
        return out; })()`);
      // ⭐️⭐️ THE COMPLAINT ITSELF: cards already marked, and the deck is
      // still there — without "show everything, including matched" ticked.
      check("a part-marked deck is still on the list, saying how far it has got",
            seen.all === false && /of 24/.test(seen.deck || ""), seen);
      check("and the deck carries a row for the back all its cards share",
            /its back/.test(seen.back || ""), seen.back);

      /* ⭐️ dropping that row on a piece says which piece is the back — of the
         whole deck, in one act, rather than card by card. */
      const dropped = await page.val(`(function () {
        var row = document.querySelector("#mList .mitem[data-back]");
        var cell = document.querySelector(".mcell");
        if (!row || !cell) return { ok: false };
        var dt = new DataTransfer();
        row.dispatchEvent(new DragEvent("dragstart", { dataTransfer: dt, bubbles: true }));
        cell.dispatchEvent(new DragEvent("drop", { dataTransfer: dt, bubbles: true, cancelable: true }));
        return { ok: true, stem: cell.dataset.stem }; })()`);
      await sleep(1500);
      const said = await fetch(`${ROOM}/api/p/${QUEUE}/wanted`).then(r => r.json());
      const now = (said.items || []).filter(i => i.id === deck.id)[0] || {};
      check("dropping the back row on a piece records it as the deck's back",
            dropped.ok && now.back === dropped.stem, { dropped, back: now.back });

      // ⭐️ and marking one more card does NOT take the deck off the list —
      // which is the whole of what was reported
      const still = await page.val(`(function () {
        var rows = document.querySelectorAll("#mList .mitem[data-id]");
        for (var i = 0; i < rows.length; i++) {
          var b = rows[i].querySelector("b");
          if (b && b.textContent === "Magic cards")
            return (rows[i].querySelector(".tag") || {}).textContent || "";
        }
        return ""; })()`);
      check("and the deck is still on the list after its back was said",
            /of 24/.test(still), still);

      /* ⭐️⭐️ AND THE LIVE DRAG, WITHOUT RELOADING THE PAGE — which is where
         the fault actually lived. link() kept the two stores it holds in step
         itself, using a SECOND, cruder rule ("any piece linked means done"),
         so the deck vanished the instant a card was dropped on it even though
         the room knew perfectly well it wanted twenty-four. It reads the
         checklist back from the room now, as the bulk bar already did. */
      // free one card again, so there is an unlinked piece on the board to
      // drop it onto — the API check before this one linked nearly all of them
      const held = await fetch(`${ROOM}/api/p/${QUEUE}/wanted`).then(r => r.json());
      const mine = ((held.items || []).filter(i => i.id === deck.id)[0] || {}).pieces || [];
      await fetch(`${ROOM}/api/p/${QUEUE}/pieces/link`,
        { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ stems: [mine[0]], wanted: "" }) });
      await page.go(`${ROOM}/p/${QUEUE}/?tab=match`);
      await sleep(900);
      const live = await page.val(`(function () {
        var row = null;
        document.querySelectorAll("#mList .mitem[data-id]").forEach(function (r) {
          var b = r.querySelector("b");
          if (b && b.textContent === "Magic cards") row = r; });
        var cell = null;
        document.querySelectorAll(".mcell").forEach(function (c) {
          if (!cell && c.dataset.stem && !/oldbox_p01_00/.test(c.dataset.stem)) cell = c; });
        if (!row || !cell) return { ok: false };
        var was = (row.querySelector(".tag") || {}).textContent || "";
        var dt = new DataTransfer();
        row.dispatchEvent(new DragEvent("dragstart", { dataTransfer: dt, bubbles: true }));
        cell.dispatchEvent(new DragEvent("drop", { dataTransfer: dt, bubbles: true, cancelable: true }));
        return { ok: true, was: was, stem: cell.dataset.stem }; })()`);
      await sleep(1800);
      const after = await page.val(`(function () {
        var got = "";
        document.querySelectorAll("#mList .mitem[data-id]").forEach(function (r) {
          var b = r.querySelector("b");
          if (b && b.textContent === "Magic cards")
            got = (r.querySelector(".tag") || {}).textContent || ""; });
        return got; })()`);
      check("dropping a card on the deck leaves it on the list, one further on",
            live.ok && /of 24/.test(after) && after !== live.was,
            { was: live.was, now: after });

      /* ⭐️⭐️ AND CALLING SOMETHING A DECK IS SAYING ITS CARDS ARE ALL
         DIFFERENT. The designer, 26 August 2026: "when something is a deck it
         should also report that each component dropped is unique in the
         checklist ie '[n] needed' rather than '1 needed'."
         ⚠️ Put back the state a pasted contents list really leaves — `each`
         stamped false, which nobody chose — because a check that cleared it
         first would be testing a list no game is ever in (fault 54). */
      const list = await fetch(`${ROOM}/api/p/${QUEUE}/wanted`).then(r => r.json());
      list.items.forEach(i => {
        if (i.name === "Spell deck") { i.each = false; delete i.each_said; }
      });
      await fetch(`${ROOM}/api/p/${QUEUE}/wanted`,
        { method: "PUT", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items: list.items, groups: list.groups || [] }) });
      await page.go(`${ROOM}/p/${QUEUE}/?tab=wanted`);
      await sleep(900);
      const row = `(function () {
        var got = null;
        document.querySelectorAll("#wBody tr").forEach(function (r) {
          var nm = r.querySelector('input[data-k="name"]');
          if (nm && nm.value === "Spell deck") got = r; });
        if (!got) return { found: false };
        return { found: true,
                 each: (got.querySelector("[data-each]") || {}).textContent || "",
                 why: (got.querySelector("td .tiny.muted") || {}).textContent || "",
                 stands: (got.querySelector("td.st .tag") || {}).textContent || "" }; })()`;
      const deckRow = await page.val(row);
      check("a deck nobody has pressed reads as all different, needing all of them",
            deckRow.found && /all different/.test(deckRow.each) &&
            /of 32/.test(deckRow.stands), deckRow);
      // ⚠️ a figure that settled itself is a figure somebody has to be able
      // to account for, so it says why in as many words
      check("and it says why, since nobody pressed anything",
            /counted as a deck/.test(deckRow.why), deckRow.why);
      // ⚠️ AND THE PRESS MUST STICK, or the room's own default puts it
      // straight back and the button looks broken — fault 50's shape.
      await page.val(`(function () {
        var b = null;
        document.querySelectorAll("#wBody tr").forEach(function (r) {
          var nm = r.querySelector('input[data-k="name"]');
          if (nm && nm.value === "Spell deck") b = r.querySelector("[data-each]"); });
        if (b) b.click(); return !!b; })()`);
      await sleep(1200);
      const pressed = await page.val(row);
      check("pressing “one is enough” on a deck sticks, and it wants one again",
            /one is enough/.test(pressed.each) && !/of 32/.test(pressed.stands),
            pressed);

      /* ⚠️⚠️ EDIT A FIELD AND PRESS THE TOGGLE IN ONE MOVEMENT. The designer,
         26 August 2026: "I edited 'small room(6)' to note that it is 6 unique
         pieces… but despite it now showing 6, I cant seem to toggle that
         immediately… Hitting the toggle doesn't seem to do anything."
         Clicking the button BLURS the box, so the box's own save fires first
         and a second save follows from the press — two writes of the whole
         list in flight at once, each replacing the page's copy when it
         answers. Whichever lands last wins, and it is not always the press. */
      const race = await page.val(`(function () {
        var row = null;
        document.querySelectorAll("#wBody tr").forEach(function (r) {
          var nm = r.querySelector('input[data-k="name"]');
          if (nm && nm.value === "Spell deck") row = r; });
        if (!row) return { found: false };
        var qty = row.querySelector('input[data-k="qty"]');
        qty.value = "6";
        qty.dispatchEvent(new Event("change", { bubbles: true }));   // the blur
        row.querySelector("[data-each]").click();                    // and the press
        return { found: true }; })()`);
      await sleep(2500);
      const settled = await page.val(row);
      check("editing a field and pressing the toggle in one movement still toggles",
            race.found && /all different/.test(settled.each) &&
            /of 6/.test(settled.stands), settled);
      // ⚠️ and the disk agrees with the screen, or the next load undoes it
      const disk = await fetch(`${ROOM}/api/p/${QUEUE}/wanted`).then(r => r.json());
      const sd = (disk.items || []).filter(i => i.name === "Spell deck")[0] || {};
      check("and the room has it written down the same way",
            sd.each === true && sd.qty === "6" && sd.need === 6,
            { each: sd.each, qty: sd.qty, need: sd.need });

      /* ⚠️⚠️ AND IT STILL WORKS IN FRONT OF AN OLDER ROOM. The pages are read
         fresh off the disk on every request; the Python is whatever was
         loaded when the room started (fault 38). So a page that quietly
         depends on a field a running room does not send yet gets `undefined`
         — and this control then said "one is enough" on everything and never
         changed, whatever you pressed. Falling back to the stored `each` is
         what makes it behave as it always did until the room is restarted. */
      // ⚠️ the page's own functions are not on `window`, so this asks the
      // question the way a person would: press it twice and it must come back
      // to where it started. A control that answers `!undefined` for ever
      // sticks on "all different" and never returns.
      const twice = [];
      for (let i = 0; i < 2; i++) {
        await page.val(`(function () {
          var b = null;
          document.querySelectorAll("#wBody tr").forEach(function (r) {
            var nm = r.querySelector('input[data-k="name"]');
            if (nm && nm.value === "Spell deck") b = r.querySelector("[data-each]"); });
          if (b) b.click(); return !!b; })()`);
        await sleep(1200);
        twice.push((await page.val(row)).each);
      }
      check("and the toggle really is a toggle — two presses come back",
            twice[0] !== twice[1] && /one is enough|all different/.test(twice[1]),
            twice);
    }

    {
      console.log("\nputting a set by for later, from the page");
      await page.go(`${ROOM}/p/the-spare-room/?tab=sheets`);
      const before = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f="todo"]');
        if (f) f.click();
        return document.querySelectorAll(".sheets .sheet").length; })()`);
      await sleep(300);
      const put = await page.val(`(function () {
        var all = document.querySelector('#sFilter button[data-f=""]');
        if (all) all.click();
        var rows = document.querySelectorAll(".boxrow"), hit = null, b = null;
        for (var i = 0; i < rows.length; i++) {
          var w = rows[i].querySelector(".fold .what");
          if (w && /Keepers/.test(w.textContent)) hit = rows[i];
        }
        if (!hit) return { found: false };
        hit.querySelectorAll("button").forEach(function (x) {
          if (/Put this set by/.test(x.textContent)) b = x;
        });
        if (b) b.click();          // ⚠️ guarded: a click on nothing throws, and
        return { found: true, pressed: !!b }; })()`);   // one throw ends the section
      check("a set of sheets can be put by for later, from its own heading",
            put.pressed, put);
      await sleep(900);
      const after = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f="todo"]');
        if (f) f.click();
        return { todo: document.querySelectorAll(".sheets .sheet").length }; })()`);
      check("and its sheets drop out of the work still to outline",
            after.todo === before - 2, { was: before, now: after.todo });
      // ⚠️ NOTHING IS HIDDEN AND NOTHING IS DELETED: there is a chip that
      // shows exactly the sheets put by, so they can always be found again.
      const stashed = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f="later"]');
        if (f) f.click();
        return { chip: !!f, cards: document.querySelectorAll(".sheets .sheet").length }; })()`);
      check("they are still here, under a chip of their own that shows which they are",
            stashed.chip && stashed.cards === 2, stashed);
      // ⚠️ and the heading says so where every box is in front of you, or a
      // set could be put by and nothing on the page would ever say it was
      const marked = await page.val(`(function () {
        var all = document.querySelector('#sFilter button[data-f=""]');
        if (all) all.click();
        return (document.querySelector(".boxrow.later .putby") || {}).textContent || ""; })()`);
      check("and the box's own heading says it is put by, in as many words",
            /put by for later/.test(marked), marked);

      /* ⭐️⭐️ AND THE FIGURE. This set of components was made FROM that box of
         sheets, so it answers to it — one switch, not two (fault 24). */
      await page.go(`${ROOM}/p/the-spare-room/?tab=wanted`);
      await sleep(900);
      const fig = await page.val(`(function () {
        var heads = [];
        document.querySelectorAll("#wBody tr.ghead").forEach(function (tr) {
          var w = tr.querySelector(".fold .what"), f = tr.querySelector(".setfig");
          heads.push({ name: w ? w.textContent : "", fig: f ? f.textContent : "",
                       later: tr.classList.contains("later") });
        });
        return { heads: heads, pct: document.getElementById("wPct").textContent,
                 says: document.getElementById("wLater").textContent }; })()`);
      check("every set on the checklist carries its own figure",
            fig.heads.length > 0 && fig.heads.every(function (h) { return /\d+%/.test(h.fig); }),
            fig.heads);
      check("the set put by is marked as such on the checklist too",
            fig.heads.some(function (h) { return /Keepers/.test(h.name) && h.later; }),
            fig.heads);
      // ⚠️ TWO NUMBERS THAT DISAGREE IN SILENCE (fault 67): the headline is
      // about what is being cut now, so the line under it says what it left out.
      check("and the headline says what it has left out of itself",
            /put by for later/.test(fig.says || "") && /whole game/i.test(fig.says || ""),
            fig.says);
      const back = await page.val(`(function () {
        var b = null;
        document.querySelectorAll("#wBody tr.ghead").forEach(function (tr) {
          var w = tr.querySelector(".fold .what");
          if (w && /Keepers/.test(w.textContent)) {
            tr.querySelectorAll("button").forEach(function (x) {
              if (/Bring back/.test(x.textContent)) b = x;
            });
          }
        });
        if (b) b.click();
        return !!b; })()`);
      check("and the same switch is on the checklist heading, to bring it back",
            back, back);
      await sleep(1200);
      const home = await page.val(`(function () {
        return { says: document.getElementById("wLater").textContent,
                 later: !!document.querySelector("#wBody tr.ghead.later") }; })()`);
      check("bringing it back counts it again, and the line about it goes",
            home.says === "" && !home.later, home);
    }

    /* ⭐️⭐️ THE CHECKLIST LEARNT FROM WHAT IS CUT. The inverse of Match, for
       a game whose contents list nobody has typed out — which is most games.
       ⚠️ The GROUPING is done in the page, off the same look-alike rule the
       review uses, so this is where it has to be checked: the room's side is
       checked through the API in check.sh, and fault 61's lesson is that a
       check through the API is a green light over a button that does nothing. */
    {
      console.log("\nlearning the checklist from the pieces already cut");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=wanted`);
      await sleep(1200);
      const shown = await page.val(`(function () {
        var b = document.getElementById("wLearnBtn") || document.getElementById("wStartLearn");
        if (b) b.click();
        return !!b; })()`);
      check("there is a way to build the list from the pieces", shown, shown);
      await sleep(2500);
      const rows = await page.val(`(function () {
        var out = [];
        document.querySelectorAll("#wLearnRows .grp").forEach(function (r) {
          out.push({ said: (r.querySelector(".said") || {}).textContent || "",
                     pics: r.querySelectorAll(".pics img").length,
                     each: (r.querySelector(".leach") || {}).textContent || "" });
        });
        return { rows: out, says: document.getElementById("wLearnSays").textContent }; })()`);
      check("the pieces that answer to nothing are gathered into groups",
            rows.rows.length >= 1, rows.rows.length);
      check("and each group says how many pieces and how many designs it holds",
            rows.rows.every((r) => /\d+ piece/.test(r.said) &&
                                   /design/.test(r.said)), rows.rows);
      /* ⭐️ ONE IS ENOUGH, UNLESS EVERY ONE IS DIFFERENT (fault 36) — the one
         thing a printed contents list can never tell you, and the one thing
         the pieces themselves CAN. It is offered, not decided: it is a
         control, and pressing it changes the answer. */
      check("and offers an answer to whether one of them is enough",
            rows.rows.every((r) => /all different|one is enough/.test(r.each)),
            rows.rows.map((r) => r.each));
      check("and it says plainly that nothing is added until you name something",
            /not added/.test(rows.says || "") && /Nothing is cut/.test(rows.says || ""),
            rows.says);
      /* ⭐️ A NAME ALREADY TYPED IS OFFERED BACK. Where every named piece in a
         group agrees about what it is called, the box arrives filled in —
         there is no sense making somebody type their own answer twice. ⚠️ Only
         where they agree: two names in a group is a question, and the room
         does not answer questions about what a thing is called. */
      check("a group whose pieces are already named offers that name back",
            rows.rows.length && (await page.val(
              `(document.querySelector("#wLearnRows input.lname") || {}).value`)),
            await page.val(`(document.querySelector("#wLearnRows input.lname") || {}).value`));

      // ⚠️ NAMING IS THE ONE THING THE ROOM CANNOT DO. A group with no name is
      // a group nobody has decided about, and must not be added.
      const was = await page.val(`({ rows:
        document.querySelectorAll("#wBody tr input[data-k=name]").length })`);
      const refused = await page.val(`(function () {
        document.querySelectorAll("#wLearnRows input.lname").forEach(function (i) {
          i.value = ""; i.dispatchEvent(new Event("input"));
        });
        document.getElementById("wLearnGo").click(); return true; })()`);
      await sleep(900);
      // ⚠️ this game already has a checklist, so what must not change is the
      // NUMBER of components on it
      const nothing = await page.val(`(function () { return {
        rows: document.querySelectorAll("#wBody tr input[data-k=name]").length,
        said: (document.querySelector(".flash") || {}).textContent || "" }; })()`);
      check("pressing Add with nothing named adds nothing, and says why",
            nothing.rows === was.rows && /cannot know what a piece is called/.test(nothing.said),
            [was.rows, nothing]);
      // and now name one group and add it
      await page.val(`(function () {
        var one = document.querySelector("#wLearnRows input.lname");
        one.value = "A learnt component";
        one.dispatchEvent(new Event("input"));
        document.getElementById("wLearnGo").click(); return true; })()`);
      await sleep(2500);
      const landed = await page.val(`(function () { return {
        names: Array.prototype.map.call(document.querySelectorAll("#wBody tr input[data-k=name]"),
          function (i) { return i.value; }),
        gone: document.getElementById("wLearn").hidden }; })()`);
      check("naming one group and pressing Add puts it on the checklist",
            (landed.names || []).indexOf("A learnt component") >= 0, landed.names);
      const kept = await (await fetch(`${ROOM}/api/p/${PROJECT}/wanted`)).json();
      const it = (kept.items || []).filter((i) => i.name === "A learnt component")[0];
      check("with the pieces of that group tied to it",
            it && (it.pieces || []).length >= 1, it && (it.pieces || []).length);
      check("so the checklist counts it as cut, off the pieces it was made from",
            it && (it.state === "cut"), it && it.state);
    }

    /* ⭐️⭐️ A WAY IN TO A SECTION OF THE CHECKLIST ITSELF. The designer, 25
       August 2026: "very obvious quirk I just noticed - I cant see how to add
       a new section to the checklist (eg to add details of the new sail set I
       just uploaded and have started cutting)." Every door made a set on the
       way past to something else. */
    {
      console.log("\nadding a section to the checklist");
      await page.go(`${ROOM}/p/the-spare-room/?tab=wanted`);
      await sleep(900);
      const opened = await page.val(`(function () {
        window.prompt = function () { return "A section of its own"; };
        var b = document.getElementById("wSetAdd");
        if (b) b.click();
        var pick = document.getElementById("wNewSetPick");
        return { there: !!b, open: !!(pick && !document.getElementById("wNewSet").hidden),
                 offers: pick ? Array.prototype.map.call(pick.options, function (o) {
                   return o.value; }) : [] }; })()`);
      check("there is a button on the checklist for adding a section",
            opened.there && opened.open, opened);
      check("and it offers the boxes of sheets, or a name of your own",
            (opened.offers || []).indexOf("__new") >= 0, opened.offers);
      await page.val(`(function () {
        document.getElementById("wNewSetPick").value = "__new";
        document.getElementById("wNewSetGo").click(); return true; })()`);
      await sleep(1500);
      const made = await page.val(`(function () {
        var heads = [];
        document.querySelectorAll("#wBody tr.ghead .fold .what").forEach(function (w) {
          heads.push(w.textContent); });
        return { heads: heads,
                 empty: (document.querySelector("#wBody tr.ghead + tr td.muted") || {}).textContent || "" };
      })()`);
      /* ⚠️ THE SECTION IS EMPTY, and a list that only draws a heading where
         there are rows under it would have made it, saved it, and then shown
         nothing at all — fault 44's shape, the thing you have just made being
         the one thing you cannot see. */
      check("the new section appears on the list at once, empty though it is",
            made.heads.indexOf("A section of its own") >= 0, made.heads);
      check("and it says what to do next, rather than being a blank space",
            /Nothing in this section yet/.test(made.empty || ""), made.empty);
      const kept2 = await (await fetch(`${ROOM}/api/p/the-spare-room/wanted`)).json();
      check("and it is written down, so it is still there on the next load",
            (kept2.groups || []).some((g) => g.name === "A section of its own"),
            (kept2.groups || []).map((g) => g.name));
    }

    /* ⭐️⭐️ A WHOLE BOX OF SHEETS OUT AGAIN, IN ONE PRESS. The designer, 25 August
       2026: "I'd like to be able to remove a full set of imported sheets in
       one click (after a confirmation)."
       ⚠️ This one really deletes, so it is done in the game kept aside for
       it, on the box kept aside for the browser. */
    {
      console.log("\ntaking a whole box of sheets out, from the page");
      await page.go(`${ROOM}/p/the-spare-room/?tab=sheets`);
      const asked = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f=""]');
        if (f) f.click();
        var said = null;
        window.confirm = function (t) { said = t; return false; };
        var rows = document.querySelectorAll(".boxrow");
        for (var i = 0; i < rows.length; i++) {
          if (/browser-fodder/.test(rows[i].querySelector(".fold .what").textContent)) {
            /* ⚠️ FOUND BY WHAT IT SAYS, NOT BY WHERE IT SITS. This pressed
               the third button in the row, and the day a fourth was added to
               the heading it pressed the wrong one — the check went red over
               code that was perfectly well. A handle that is a position will
               drift; the words on the button are the thing being tested. */
            var rm = null;
            rows[i].querySelectorAll("button").forEach(function (b) {
              if (/Remove this set/.test(b.textContent)) rm = b;
            });
            if (rm) rm.click();
            return { said: said, heads: rows.length, found: !!rm };
          }
        }
        return { said: null, heads: rows.length }; })()`);
      // ⚠️ EVERYTHING IT WILL DO, BEFORE IT IS ANSWERED — this is the one
      // action in the room that really deletes
      check("removing a box asks first, and says how many sheets would go",
            /Take all 2 sheets/.test(asked.said || ""), asked.said);
      check("and says what it cannot put back, rather than promising an undo",
            /imported again/.test(asked.said || "") &&
            /outlines drawn on them are kept/.test(asked.said || ""), asked.said);
      check("and saying no leaves every sheet where it was",
            (await (await fetch(`${ROOM}/api/p/the-spare-room`)).json())
              .sheets.filter((x) => x.id.indexOf("browser-fodder") === 0).length === 2);
      await page.val(`(function () {
        window.confirm = function () { return true; };
        var rows = document.querySelectorAll(".boxrow");
        for (var i = 0; i < rows.length; i++) {
          if (/browser-fodder/.test(rows[i].querySelector(".fold .what").textContent)) {
            var rm = null;                       // by its words, not its place
            rows[i].querySelectorAll("button").forEach(function (b) {
              if (/Remove this set/.test(b.textContent)) rm = b;
            });
            if (rm) rm.click();
            return !!rm; } }
        return false; })()`);
      await sleep(2000);
      const left = await (await fetch(`${ROOM}/api/p/the-spare-room`)).json();
      check("and saying yes takes the whole box out in one press",
            !left.sheets.filter((x) => x.id.indexOf("browser-fodder") === 0).length,
            left.sheets.map((x) => x.id));
      check("while the other boxes are left exactly as they were",
            left.sheets.filter((x) => x.id.indexOf("keepers") === 0).length === 2,
            left.sheets.map((x) => x.id));
    }

    /* ⭐️⭐️ ONE DRAG, ONE SET. The designer, 25 August 2026: "I just imported 12 new
       files into the project, assuming they would all stay together as a
       single set of 12 sheets, but they've all turned into separate sets,
       which is highly inefficient. I think it is a reasonable view that files
       imported in one go will form a single set."
       ⭐️ Two halves: what a handful of dropped files is CALLED (one rule, in
       room/drop.js, because both ways in use it), and putting right the ones
       that came in before that was true. */
    {
      console.log("\nfiles dropped in one go make one set");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const named = await page.val(`(function () {
        function fake(n, p) { return { name: n, _path: p }; }
        return {
          folder: RoomDrop.setFor([fake("a.pdf", "The Core Box/a.pdf"),
                                   fake("b.pdf", "The Core Box/b.pdf")]),
          shared: RoomDrop.setFor([fake("sail-01.png"), fake("sail-02.png"),
                                   fake("sail-03.png")]),
          nothing: RoomDrop.setFor([fake("scan001.png"), fake("qq.png")]),
          alone: RoomDrop.setFor([fake("just-the-one.pdf")]) }; })()`);
      check("a dropped folder gives its name to the set",
            named.folder && named.folder.name === "The Core Box" &&
            named.folder.prefix === "the-core-box", named.folder);
      // ⭐️ the commonest case of all: a dozen scans named alike
      check("and files named alike are gathered under the part they share",
            named.shared && named.shared.prefix === "sail", named.shared);
      check("with nothing to go on, the set is the day it arrived, not nonsense",
            named.nothing && /^Imported \d/.test(named.nothing.name || ""), named.nothing);
      // ⚠️ one file is its own set already; a prefix would invent a heading
      check("and one file on its own is left exactly as it was",
            named.alone === null, named.alone);
    }

    /* ⭐️⭐️ AND PUTTING RIGHT WHAT CAME IN BEFORE. The sheets SHOWN are the
       sheets acted on, so the search box is how they are chosen. */
    {
      console.log("\ngathering sheets that are already in the game into one set");
      await page.go(`${ROOM}/p/the-spare-room/?tab=sheets`);
      const joined = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f=""]');
        if (f) f.click();
        document.getElementById("sFind").value = "keepers";
        document.getElementById("sFind").dispatchEvent(new Event("input"));
        return true; })()`);
      await sleep(700);
      const asked = await page.val(`(function () {
        var said = null;
        window.prompt = function (t, guess) { said = { t: t, guess: guess }; return "The Sail Sheets"; };
        var b = document.getElementById("sJoin");
        var says = b.textContent;
        b.click();
        return { says: says, said: said }; })()`);
      check("the button says how many sheets it would gather",
            /Put these 2 into one set/.test(asked.says || ""), asked.says);
      check("and it offers a name made from what they are called already",
            asked.said && /keepers/i.test(asked.said.guess || ""), asked.said && asked.said.guess);
      check("and says plainly that nothing is renamed",
            asked.said && /Nothing is renamed/.test(asked.said.t || ""),
            asked.said && (asked.said.t || "").slice(0, 60));
      await sleep(1600);
      const after = await (await fetch(`${ROOM}/api/p/the-spare-room`)).json();
      const mine = (after.sheets || []).filter((x) => x.id.indexOf("keepers") === 0);
      check("the sheets shown are gathered into one set",
            mine.length === 2 && mine.every((x) => x.book === "the-sail-sheets"),
            mine.map((x) => [x.id, x.book]));
      // ⚠️⚠️ AND NOT ONE ID CHANGED. Pieces are named from the sheet id and
      // the outlines are filed under it; a set is a label, not a move.
      check("and not one sheet id changed, which is what pieces are named from",
            mine.map((x) => x.id).join(",") === "keepers-01,keepers-02",
            mine.map((x) => x.id));
      check("the room calls that set by the name it was given",
            (after.books || {})["the-sail-sheets"] === "The Sail Sheets", after.books);
      // ⭐️ and it undoes: the same press with an empty name
      await page.val(`(function () {
        window.prompt = function () { return ""; };
        document.getElementById("sJoin").click(); return true; })()`);
      await sleep(1600);
      const back = await (await fetch(`${ROOM}/api/p/the-spare-room`)).json();
      check("and an empty name puts them back in the sets their files gave them",
            (back.sheets || []).filter((x) => x.id.indexOf("keepers") === 0)
              .every((x) => !x.book), (back.sheets || []).map((x) => [x.id, x.book]));
    }

    /* ⭐️⭐️ NAMING THE BOX A SET OF SHEETS CAME OUT OF. The designer, 25 August
       2026: "Ability to rename imported sections... I need to rename them from
       their current file names (which are lots of nonsense)." */
    {
      console.log("\nnaming a box of sheets, from the page");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=sheets`);
      const before = await page.val(`(function () {
        var f = document.querySelector('#sFilter button[data-f=""]');
        if (f) f.click();
        return Array.prototype.map.call(document.querySelectorAll(".boxrow"), function (r) {
          return { name: r.querySelector(".fold .what").textContent,
                   says: r.querySelector("button.rename").textContent }; }); })()`);
      check("every box of sheets offers a name of its own",
            before.length >= 2 &&
            before.every((h) => /Name this set|Rename/.test(h.says || "")), before);
      await page.val(`(function () {
        window.prompt = function () { return "The Odd One"; };
        var rows = document.querySelectorAll(".boxrow");
        for (var i = 0; i < rows.length; i++) {
          if (/odd-one-out/.test(rows[i].querySelector(".fold .what").textContent)) {
            rows[i].querySelector("button.rename").click(); return true;
          }
        }
        return false; })()`);
      await sleep(1800);
      const after = await page.val(`(function () {
        return { heads: Array.prototype.map.call(document.querySelectorAll(".boxrow .fold .what"),
                   function (h) { return h.textContent; }),
                 sheet: (document.querySelector('.sheet .body b') || {}).textContent || "" }; })()`);
      check("naming one changes what the room calls it",
            (after.heads || []).indexOf("The Odd One") >= 0, after.heads);
      // ⚠️ and the sheets under it, because the file name is on every card too
      const said = await (await fetch(`${ROOM}/api/p/${PROJECT}`)).json();
      const odd = (said.sheets || []).filter((x) => x.id.indexOf("odd-one-out") === 0)[0] || {};
      check("and the sheets in it are called by it as well",
            /^The Odd One/.test(odd.label || ""), odd.label);
      // put the bench back exactly as it was
      await fetch(`${ROOM}/api/p/${PROJECT}/book/odd-one-out`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "" }) });
    }

    /* ⭐️⭐️ ONE SET TAKEN AWAY ON ITS OWN, FROM THE BUTTON. The designer, 26
       August 2026: "I'd like to be able to just export a set of cut pieces,
       rather than everything in one project folder." What the room writes is
       checked through the API in check.sh; what is checked HERE is the wire —
       that the set chosen on the page is the set that gets written. Fault 61:
       a check through the API is a green light over a button that does
       nothing. */
    if (BED) {
      console.log("\ntaking one set away, from the button");
      await page.go(`${ROOM}/p/${PROJECT}/?tab=export`);
      await sleep(1800);
      const picker = await page.val(`(function () {
        var s = document.getElementById("exportSet");
        return { has: !!s, n: s ? s.options.length : 0,
                 all: s && s.options[0] ? s.options[0].textContent : "" }; })()`);
      check("the way out offers the whole game, or one set of it",
            picker && picker.has && picker.n >= 2 &&
            /everything in this game/.test(picker.all || ""), picker);
      const chose = await page.val(`(function () {
        var s = document.getElementById("exportSet");
        s.value = "proving-ground-sheets";
        s.dispatchEvent(new Event("change"));
        return { where: document.getElementById("exportWhere").textContent,
                 says: document.getElementById("exportGo").textContent }; })()`);
      // ⚠️ the folder's name comes from the room, not worked out in the page:
      // two spellings of it would show one folder and fill another
      check("choosing one names the folder it will go into, and says so on the button",
            chose && /export-proving-ground-sheets$/.test(chose.where || "")
            && /this set/.test(chose.says || ""), chose);
      const out = path.join(BED, "export-proving-ground-sheets");
      fs.rmSync(out, { recursive: true, force: true });
      await page.val(`document.getElementById("exportGo").click(); true`);
      for (let i = 0; i < 80; i++) {
        if (fs.existsSync(path.join(out, "inventory.csv"))) break;
        await sleep(400);
      }
      check("and pressing it writes THAT set's folder",
            fs.existsSync(path.join(out, "inventory.csv")), fs.existsSync(out));
      fs.rmSync(out, { recursive: true, force: true });
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
      /* ⚠️ AND NO MASK OFF TOOL EITHER. A baked page cannot re-draft itself —
         its suggestions were worked out when it was made and there is no room
         behind it to ask again — so the tool would be a control that quietly
         does nothing, which is fault 58 exactly. It is not offered where it
         cannot work. ⚠️ `hidden` alone does not hide a button whose CSS sets
         `display` (fault 23), so this measures the button rather than
         believing the flag. */
      const noMask = await page.val(`(function () {
        var b = document.getElementById("tSkip");
        return { there: !!b, seen: !!b && b.offsetWidth > 0 }; })()`);
      check("and no Mask off tool, which needs a room to re-draft the sheet",
            noMask && noMask.there && !noMask.seen, noMask);
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
