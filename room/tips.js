/* Every control says what it does.
 *
 * ⭐️ THE DESIGNER, 23 August 2026: "adding helpful instructional text to my platforms
 * like Cutting Room. I don't, for example, have any idea what 'straight to the
 * table' means on the project selection screen, so a hover tool or just in
 * line text popup or whatever explaining what all the features and buttons do
 * would be very helpful. And that's not just for me, obviously!"
 *
 * They are right, and it is the same complaint as every other one they have made:
 * the room knows something the person using it does not, and does not say it.
 *
 * How it works: put `data-tip="a plain sentence"` on ANY element and it gets
 * an explanation on hover and on keyboard focus. Nothing else to wire up —
 * the listeners are on the document, so a card built later by JavaScript is
 * covered without anybody remembering to call anything. That is fault 14's
 * lesson: a guard each handler has to remember is a guard one of them forgets.
 *
 * ⚠️ Hovering does not exist on a touch screen, and somebody who wants to
 * READ the room rather than poke at it should not have to hunt. So there is
 * also "Explain everything", which writes every tip out underneath its own
 * control, and is remembered between visits.
 */
(function () {
  var KEY = "cuttingroom.tips.on";
  var bubble = null, over = null, timer = null;

  /* ⚠️ THIS BRINGS ITS OWN LOOK, and it has to. The room's pages share
     room.css; the cutting table does not — it is one self-contained file so
     that it still works opened straight off a disk. So the first version of
     this styled the bubble in room.css, and on the table the bubble came out
     as an unstyled strip of text a page wide at the very bottom of the
     window: switched on, correct, and invisible. A thing that goes on every
     page carries its own paint.

     The colours are the page's own where it has them and plain values where
     it does not, so it sits right on both benches. */
  var PAINT = ".tipbubble{position:fixed;z-index:60;max-width:320px;" +
    "padding:8px 11px;border:1px solid var(--line,var(--rule,#26313D));" +
    "border-radius:4px;background:var(--panel-2,#1B242E);" +
    "color:var(--ink,#DCE3EB);font-size:13px;line-height:1.45;" +
    "font-family:var(--ui,system-ui,-apple-system,sans-serif);" +
    "box-shadow:0 6px 22px rgba(0,0,0,.45);opacity:0;pointer-events:none;" +
    "transition:opacity .12s}" +
    ".tipbubble.on{opacity:1}" +
    ".tipline{display:block;width:100%;flex:0 0 100%;" +
    "color:var(--dim,var(--muted,#8494A5));font-size:12px;line-height:1.4;" +
    "font-style:italic;margin:3px 0 6px}" +
    ".tipstoggle{appearance:none;border:1px solid var(--line,var(--rule,#26313D));" +
    "background:var(--panel-2,#1B242E);color:var(--dim,var(--muted,#8494A5));" +
    "border-radius:3px;font:inherit;font-size:12px;padding:3px 9px;" +
    "cursor:pointer;margin-right:4px}" +
    ".tipstoggle:hover{color:var(--ink,#DCE3EB)}" +
    '.tipstoggle[aria-pressed="true"]{color:var(--ink,#DCE3EB);' +
    "border-color:var(--brass,#C9A227)}";

  (function paint() {
    var st = document.createElement("style");
    st.textContent = PAINT;
    (document.head || document.documentElement).appendChild(st);
  })();

  /* ⭐️ A `title` IS A TIP, so take it rather than making somebody write the
     same sentence twice — fault 24, which is the one about a set of words
     written out in two places disagreeing with itself. The native tooltip is
     stood down as it is taken over, or the browser's own would show
     underneath ours. Done as each control is met, so a card built later by
     JavaScript needs nobody to remember it. */
  function take(el) {
    if (el && !el.getAttribute("data-tip") && el.getAttribute("title")) {
      el.setAttribute("data-tip", el.getAttribute("title"));
      el.removeAttribute("title");
    }
    return el;
  }

  function make() {
    if (bubble) return bubble;
    bubble = document.createElement("div");
    bubble.className = "tipbubble";
    bubble.setAttribute("role", "tooltip");
    document.body.appendChild(bubble);
    return bubble;
  }

  function show(el) {
    var text = el.getAttribute("data-tip");
    if (!text) return;
    var b = make();
    b.textContent = text;
    b.classList.add("on");
    var r = el.getBoundingClientRect();
    var w = b.offsetWidth, h = b.offsetHeight;
    // under the control by default, above it when there is no room below —
    // measured rather than guessed, because a tip that falls off the bottom
    // of the window is a tip nobody reads
    var top = r.bottom + 8;
    if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 8);
    var left = Math.min(Math.max(8, r.left), window.innerWidth - w - 8);
    b.style.top = top + "px";
    b.style.left = left + "px";
  }

  function hide() {
    if (bubble) bubble.classList.remove("on");
    over = null;
  }

  document.addEventListener("mouseover", function (ev) {
    var el = ev.target.closest ? take(ev.target.closest("[data-tip],[title]")) : null;
    if (!el || el === over) return;
    over = el;
    clearTimeout(timer);
    timer = setTimeout(function () { if (over === el) show(el); }, 180);
  });
  document.addEventListener("mouseout", function (ev) {
    var el = ev.target.closest ? ev.target.closest("[data-tip]") : null;
    if (el && el === over) { clearTimeout(timer); hide(); }
  });
  document.addEventListener("focusin", function (ev) {
    var el = ev.target.closest ? take(ev.target.closest("[data-tip],[title]")) : null;
    if (el) { over = el; show(el); }
  });
  document.addEventListener("focusout", hide);
  window.addEventListener("scroll", hide, true);
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") hide();
  });

  /* ---------------------------------------------- everything, written out */

  /* ⚠️ WRITING THE LINES CHANGES THE PAGE, AND THE WATCHER BELOW WATCHES FOR
     THE PAGE CHANGING. Without this flag it would answer its own writing for
     ever: remove every line, add them all back, be told the page changed,
     remove every line… eight times a second, until the tab was closed. */
  var writing = false;

  function lines(on) {
    writing = true;
    document.querySelectorAll(".tipline").forEach(function (x) { x.remove(); });
    if (!on) { writing = false; return; }
    document.querySelectorAll("[title]").forEach(take);
    document.querySelectorAll("[data-tip]").forEach(function (el) {
      if (el.closest(".bar") || el.dataset.tipQuiet) return;   // not the top bar
      var line = document.createElement("small");
      line.className = "tipline";
      line.textContent = el.getAttribute("data-tip");
      // beside a control that sits in a row, underneath one that does not
      (el.parentNode || document.body).insertBefore(line, el.nextSibling);
    });
    // let go on the next turn, after the changes have been reported
    setTimeout(function () { writing = false; }, 0);
  }

  function set(on) {
    document.body.classList.toggle("tips-out", !!on);
    try { localStorage.setItem(KEY, on ? "1" : "0"); } catch (e) { /* private */ }
    lines(on);
    var b = document.getElementById("tipsToggle");
    if (b) {
      b.setAttribute("aria-pressed", String(!!on));
      b.textContent = on ? "Hide the explanations" : "What does this do?";
    }
  }

  function on() {
    try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; }
  }

  document.addEventListener("DOMContentLoaded", function () {
    /* The switch goes in the row of links at the top of the room's pages.
       The cutting table has no such row — every inch of its bar is a tool and
       the sheet gets what is left — so there it is hover alone, which suits a
       tool driven by a mouse in any case. */
    var nav = document.querySelector("header.bar nav");
    if (nav) {
      var b = document.createElement("button");
      b.id = "tipsToggle";
      b.type = "button";
      b.className = "tipstoggle";
      b.setAttribute("aria-pressed", "false");
      b.title = "Explain every button on this page, in plain English";
      b.addEventListener("click", function () { set(!on()); });
      nav.insertBefore(b, nav.firstChild);
    }
    set(on());

    /* A page that builds its own cards after loading — which is every page
       here — would leave the new ones unexplained. Watch for them instead of
       asking each renderer to remember. */
    new MutationObserver(function () {
      if (!on() || writing) return;
      clearTimeout(lines.soon);
      lines.soon = setTimeout(function () { lines(true); }, 120);
    }).observe(document.body, { childList: true, subtree: true });
  });
})();
