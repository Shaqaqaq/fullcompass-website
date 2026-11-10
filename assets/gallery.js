// Full Compass website: the walk down the gallery corridor on the home page.
// The page is a flat gallery wall without this script. Here, on a screen wide enough and when the visitor has not
// asked for reduced motion, <html> gets the class "walk": scrolling moves along the corridor (assets/site.css draws
// it), the arrows and the caption step from picture to picture, and each picture is a link to its app's room.
(function () {
  "use strict";

  var hall = document.querySelector(".hall");
  if (!hall || !window.matchMedia || !window.requestAnimationFrame) return;
  if (!(window.CSS && CSS.supports && CSS.supports("transform-style", "preserve-3d"))) return;

  var root = document.documentElement;
  var view = hall.querySelector(".view");
  var world = hall.querySelector(".world");
  var hud = hall.querySelector(".hud");
  var caption = hud.querySelector(".caption");
  var dots = hud.querySelector(".dots");
  var pieces = Array.prototype.slice.call(hall.querySelectorAll(".piece"));

  // The corridor, in its own units (the stylesheet uses the same figures).
  var FIRST = 1500, GAP = 900, SEGMENT = 1400;
  var STAND = 780;                                   // how far back to stand from a picture
  var END = FIRST + GAP * pieces.length + 900;       // the end wall
  var PER_PIXEL = 1.5;                               // corridor units walked for each pixel scrolled
  var stops = pieces.map(function (p, i) { return FIRST + GAP * i - STAND; });
  stops.push(END - 750);
  var last = stops.length - 1;

  var wide = window.matchMedia("(min-width: 860px) and (min-height: 540px)");
  var still = window.matchMedia("(prefers-reduced-motion: reduce)");
  var on = false, built = false, queued = false, current = -1, look = 0, lookTo = 0, looking = false;

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function build() {
    built = true;
    // Walls, floor and ceiling, in lengths: one in front of the door, the rest to the end wall.
    for (var k = -1; k * SEGMENT < END; k++) {
      ["wl", "wr", "fl", "ce"].forEach(function (side) {
        var s = el("div", "seg " + side + (k > 2 ? " far" : ""));
        s.style.setProperty("--k", k);
        s.setAttribute("aria-hidden", "true");
        world.insertBefore(s, world.firstChild);
      });
    }
    stops.forEach(function (_, i) {
      var li = el("li"), b = el("button");
      b.type = "button";
      b.setAttribute("aria-label", i === last ? "The end of the corridor: download" : "Picture " + (i + 1) + ": " + pieces[i].getAttribute("data-name"));
      b.addEventListener("click", function () { go(i, true); });
      li.appendChild(b);
      dots.appendChild(li);
    });
    hud.querySelector(".prev").addEventListener("click", function () { go(Math.max(0, current - 1), true); });
    hud.querySelector(".next").addEventListener("click", function () { go(Math.min(last, current + 1), true); });
    var walkIn = hall.querySelector(".walk-in");
    if (walkIn) walkIn.addEventListener("click", function (e) { if (on) { e.preventDefault(); go(0, true); } });
    pieces.forEach(function (p, i) {
      p.querySelector("a").addEventListener("focus", function () { if (on && current !== i) go(i, false); });
    });
    view.addEventListener("mousemove", function (e) {
      if (!on) return;
      lookTo = (e.clientX / window.innerWidth - 0.5) * 5;
      if (!looking) { looking = true; requestAnimationFrame(turn); }
    });
    document.addEventListener("keydown", function (e) {
      if (!on || e.altKey || e.ctrlKey || e.metaKey) return;
      var r = hall.getBoundingClientRect();
      if (r.top > 1 || r.bottom < window.innerHeight) return;         // only while inside the corridor
      if (e.key === "ArrowRight") { e.preventDefault(); go(Math.min(last, current + 1), true); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(Math.max(0, current - 1), true); }
    });
  }

  function turn() {
    look += (lookTo - look) * 0.12;
    world.style.setProperty("--look", look.toFixed(3) + "deg");
    if (Math.abs(lookTo - look) > 0.01 && on) requestAnimationFrame(turn); else looking = false;
  }

  function hallTop() { return hall.getBoundingClientRect().top + window.pageYOffset; }

  function go(i, smooth) {
    window.scrollTo({ top: hallTop() + stops[i] / PER_PIXEL, behavior: smooth && !still.matches ? "smooth" : "auto" });
  }

  function fromHash() {
    var m = /^#room-(\d+)$/.exec(location.hash);
    if (!on || !m || stops[m[1] - 1] == null) return false;
    go(m[1] - 1, false);
    return true;
  }

  function size() {
    var s = Math.min(window.innerWidth / 1440, window.innerHeight / 880);
    view.style.setProperty("--s", Math.max(0.5, s).toFixed(4));
  }

  function describe(i) {
    caption.textContent = "";
    var small = el("small"), a = el("a");
    if (i === last) {
      small.textContent = "The end of the corridor";
      a.href = "/download/";
      a.textContent = "Download for Windows";
    } else {
      var p = pieces[i];
      small.textContent = (i < 9 ? "0" : "") + (i + 1) + " of 0" + pieces.length + " · " + p.getAttribute("data-kind");
      a.href = p.querySelector("a").getAttribute("href");
      a.textContent = p.getAttribute("data-name");
    }
    caption.appendChild(small);
    caption.appendChild(a);
    Array.prototype.forEach.call(dots.querySelectorAll("button"), function (b, n) {
      if (n === i) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current");
    });
    hud.querySelector(".prev").disabled = i === 0;
    hud.querySelector(".next").disabled = i === last;
  }

  function frame() {
    queued = false;
    if (!on) return;
    var walk = Math.min(Math.max(-hall.getBoundingClientRect().top, 0), stops[last] / PER_PIXEL) * PER_PIXEL;
    world.style.setProperty("--walk", walk.toFixed(1) + "px");
    var intro = Math.min(Math.max(1 - walk / 320, 0), 1);
    view.style.setProperty("--intro", intro.toFixed(3));
    view.classList.toggle("entered", intro === 0);
    hud.inert = intro > 0.5;
    // A picture the visitor has walked past is put away, so it cannot be seen or chosen from behind.
    pieces.forEach(function (p, i) {
      var past = walk - (FIRST + GAP * i);
      p.style.opacity = past > -260 ? Math.max(0, 1 - (past + 260) / 300).toFixed(2) : "";
      p.style.visibility = past > 40 ? "hidden" : "";
    });
    var nearest = 0;
    stops.forEach(function (s, i) { if (Math.abs(s - walk) < Math.abs(stops[nearest] - walk)) nearest = i; });
    if (nearest !== current) { current = nearest; describe(current); }
  }

  // Scroll events already come once a frame, so the corridor is moved at once (a hidden tab holds animation frames back).
  function queue() { frame(); }

  function set() {
    var want = wide.matches && !still.matches;
    if (want === on) { if (on) { size(); queue(); } return; }
    on = want;
    root.classList.toggle("walk", on);
    hud.hidden = !on;
    if (on) {
      if (!built) build();
      hall.style.setProperty("--track", Math.ceil(stops[last] / PER_PIXEL) + "px");
      world.style.setProperty("--end", END);
      size();
      current = -1;
      // The pictures' ids are for the flat wall: here the browser's own jump to one would land anywhere along the
      // corridor, so they come off, and /#room-3 (the way back from a room) is followed by hand.
      pieces.forEach(function (p) { p.removeAttribute("id"); });
      if (fromHash()) {
        requestAnimationFrame(fromHash);
        window.addEventListener("load", fromHash, { once: true });
      }
      queue();
    } else {
      pieces.forEach(function (p, i) { p.style.visibility = ""; p.style.opacity = ""; p.id = "room-" + (i + 1); });
      view.classList.remove("entered");
    }
  }

  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", set);
  window.addEventListener("hashchange", fromHash);
  [wide, still].forEach(function (q) {
    if (q.addEventListener) q.addEventListener("change", set); else if (q.addListener) q.addListener(set);
  });
  set();
})();
