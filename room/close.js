/* Closing the Cutting Room, from the Cutting Room.
 *
 * ⭐️ The designer, 22 August 2026: "a simpler way to open and quit. I don't like
 * terminal at the best of times." Quitting used to mean finding the Terminal
 * window the room was started from and closing it. They are already looking at
 * the room in a browser, so the room closes itself from here.
 *
 * ⚠️ Nothing here may cut a save short. Fault 1 — the fault this whole tool
 * exists because of — is work that stayed in the browser and never reached
 * the disk. So before it closes, the room is asked what is still in flight:
 * an import or a cut running on a thread, or a cutting table open in another
 * tab with an edit not yet written down. Anything holding is named, in plain
 * English, and the person decides.
 *
 * Shared by the front page and a project's page.
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* The room has gone. There is no server left to serve a page, so this page
     rewrites itself into the closed sign. */
  function closedSign(how) {
    document.title = "The Cutting Room is closed";
    var main = document.createElement("div");
    main.className = "closedroom";
    main.innerHTML =
      "<h1>The Cutting Room is closed.</h1>" +
      "<p>Everything you cut and everything you named is on the disk, where it was " +
      "all along. Nothing was kept in this browser.</p>" +
      "<p class=\"how\">" + esc(how || "Open it again by running cutting_room.py.") + "</p>" +
      "<p class=\"tiny muted\">This page is just a sign on the door — there is nothing " +
      "behind it now. You can close the tab.</p>";
    document.body.innerHTML = "";
    document.body.appendChild(main);
  }

  /* What is in flight, as a question a person can answer.
     ⚠️ ONE GUARD FOR BOTH DOORS. Starting the room again IS closing it, with
     a promise attached — so it asks exactly what closing asks, and only the
     last line differs. Two copies of this question would drift apart, and the
     one that drifted would be the one that lost somebody's work. */
  function ask(reasons, again) {
    var lines = reasons.map(function (r) { return "  • " + r.what; });
    var hold = reasons.some(function (r) { return r.hold; });
    return window.confirm(
      (hold ? "Something is still being written down:\n\n"
            : "The room is quiet, but this is still open:\n\n") +
      lines.join("\n") + "\n\n" +
      (hold ? (again ? "Starting it again now could lose it. Start it again anyway?"
                     : "Closing now could lose it. Close the room anyway?")
            : (again ? "Start the Cutting Room again?" : "Close the Cutting Room?")));
  }

  function close() {
    fetch("/api/busy")
      .then(function (r) { return r.json(); })
      .then(function (b) {
        var reasons = b.reasons || [];
        if (reasons.length && !ask(reasons, false)) return null;
        return fetch("/api/close", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ force: reasons.length > 0 })
        }).then(function (r) { return r.json(); });
      })
      .then(function (j) {
        if (!j) return;
        if (j.error) { window.alert("The room could not close itself: " + j.error); return; }
        // It said it would go. Give the server the half-second it asked for,
        // then put the sign up — by which time there is nothing to fetch.
        if (j.closed) setTimeout(function () { closedSign(j.how); }, 700);
      })
      .catch(function () {
        // No answer at all almost always means it has already gone.
        closedSign("");
      });
  }

  /* ⭐️⭐️ STARTING THE ROOM AGAIN, FROM THE ROOM. The designer, 24 August 2026: "is
     there a way to build a relaunch button into the browser tab it uses
     somehow?" — asked after being told twice in a day to close the room and
     open it again, because it was running older code than its own pages
     (fault 38). The advice is right; the errand is the problem, since it
     means going to find a Terminal window they never wanted to see.

     The room stops and starts itself in place: same window, same port, same
     command, and a NEW process — which is the entire point, because a running
     program cannot re-read itself. This page then waits for a room that says
     it started at a different moment from the one that answered here, and
     only then reloads. Waiting for "it answers" is not enough: the old room
     answers perfectly well right up until it goes. */
  function waiting(said) {
    var box = document.getElementById("roomAgain");
    if (!box) {
      box = document.createElement("div");
      box.id = "roomAgain";
      // ⚠️ its own paint: this must look right on any page that loads this
      // script, whether or not that page has the room's stylesheet (fault 32)
      box.setAttribute("style",
        "position:fixed;inset:0;z-index:9999;display:flex;align-items:center;" +
        "justify-content:center;background:rgba(12,12,14,.86);color:#f2f2f2;" +
        "font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;text-align:center;padding:24px");
      document.body.appendChild(box);
    }
    box.innerHTML = '<div style="max-width:34em">' + said + "</div>";
    return box;
  }

  function waitForTheNewRoom(was, how) {
    waiting("<b>The Cutting Room is starting again…</b><br><br>" +
            "The same window, the same address. Everything you cut and named " +
            "is on the disk; this page will come back by itself.");
    var tries = 0;
    var timer = setInterval(function () {
      tries += 1;
      fetch("/api/health", { cache: "no-store" })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          // ⚠️ a DIFFERENT room, not merely an answer: the old one is still
          // answering for the half second before it goes
          if (j && j.started && j.started !== was) {
            clearInterval(timer);
            location.reload();
          }
        })
        .catch(function () { /* between the two rooms; keep asking */ });
      if (tries > 60) {                     // about forty seconds
        clearInterval(timer);
        waiting("<b>The room has not come back.</b><br><br>" +
                "Nothing is at risk — everything cut and named is on the disk. " +
                esc(how || "Open it again the way you opened it.") +
                "<br><br><a href=\"/\" style=\"color:#9cf\">Try this page again</a>");
      }
    }, 700);
  }

  function relaunch() {
    fetch("/api/busy")
      .then(function (r) { return r.json(); })
      .then(function (b) {
        var reasons = b.reasons || [];
        if (reasons.length && !ask(reasons, true)) return null;
        return fetch("/api/relaunch", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ force: reasons.length > 0 })
        }).then(function (r) { return r.json(); });
      })
      .then(function (j) {
        if (!j) return;
        // ⚠️ THE ROOM REFUSED, AND IT IS STILL RUNNING — say so plainly, or a
        // person who has just been told to restart will think they did
        if (j.wont_start) {
          window.alert("The room has NOT been restarted, and it is still " +
                       "running as it was.\n\n" + j.wont_start +
                       "\n\nIt read the new code before letting go of the old " +
                       "room, and would not have been able to start again.");
          return;
        }
        if (j.error) { window.alert("The room could not start itself again: " + j.error); return; }
        if (j.relaunching) waitForTheNewRoom(j.was, j.how);
      })
      .catch(function () {
        window.alert("The room did not answer. Nothing has been restarted.");
      });
  }

  function install() {
    var nav = document.querySelector("header.bar nav");
    if (!nav || nav.querySelector("#closeRoom")) return;
    var a = document.createElement("a");
    a.href = "#";
    a.id = "closeRoom";
    a.className = "closelink";
    a.textContent = "Close the Cutting Room";
    a.title = "Stop the room. Everything cut and named stays on the disk.";
    a.addEventListener("click", function (e) { e.preventDefault(); close(); });
    var r = document.createElement("a");
    r.href = "#";
    r.id = "againRoom";
    r.className = "closelink";
    r.textContent = "Start it again";
    r.title = "Stop the room and start it straight back up, in the same window " +
              "at the same address — which is how the room picks up any change " +
              "to its own code. Nothing is cut, nothing is deleted, and this " +
              "page comes back by itself.";
    r.addEventListener("click", function (e) { e.preventDefault(); relaunch(); });
    nav.appendChild(r);
    nav.appendChild(a);
  }

  /* ⭐️⚠️ A ROOM RUNNING YESTERDAY'S CODE MUST SAY SO.
     The designer, 23 August 2026, pressing a button built that afternoon: "when I
     press 'Split it' I get a 'no such call' error."

     They had left the room open for hours. Its pages are read off the disk on
     every request, so the new button was there; its Python is whatever was
     loaded when the process started, so the route behind the button was not.
     A running program cannot re-read itself, and nothing said so — the button
     simply looked broken.

     ⚠️ It is a BANNER, not a console message. The person who needs to read
     this is the one looking at the page, and the room has to be closed and
     opened again before anything built since will work. */
  function sayIfStale() {
    fetch("/api/health")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.stale || document.getElementById("staleRoom")) return;
        var bar = document.createElement("div");
        bar.id = "staleRoom";
        bar.className = "staleroom";
        bar.innerHTML =
          "<b>This room is running older code than these pages.</b> " +
          "The Cutting Room has been updated since it was opened, and a page " +
          "is read fresh every time while the room itself is not — so a button " +
          "added since may answer <i>no such call</i>. " +
          "<b>Start it again</b> and it will work. " +
          "Nothing is at risk: everything cut and named is on the disk. ";
        // ⭐️ AND THE BUTTON RIGHT HERE, because this banner is the one place
        // in the room where somebody has just been told to do something and
        // had to go and find a Terminal window to do it.
        var go = document.createElement("button");
        go.type = "button";
        go.textContent = "Start the room again now";
        go.title = "Stop the room and start it straight back up, in the same " +
                   "window at the same address, so it is running the code that " +
                   "is on the disk now. This page comes back by itself.";
        go.addEventListener("click", function () { relaunch(); });
        bar.appendChild(go);
        document.body.insertBefore(bar, document.body.firstChild);
      })
      .catch(function () { /* the room has gone; the closed sign covers that */ });
  }

  window.RoomClose = { install: install, close: close, sign: closedSign,
                       stale: sayIfStale, again: relaunch };
  // ?closedsign=1 puts the sign up without closing anything, so it can be
  // photographed. The same trick as ?probe=1 and ?dropprobe=1.
  if (/[?&]closedsign=1/.test(location.search)) {
    setTimeout(function () { closedSign("Double-click Cutting Room to open it again."); }, 30);
  }
  function start() { install(); sayIfStale(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
