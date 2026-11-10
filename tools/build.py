#!/usr/bin/env python3
"""Builds the website: each page in src/pages gets the shared head, header and footer from src/partials, and is
written where GitHub Pages serves it (src/pages/apps.html -> apps/index.html, index.html -> index.html).
Then every internal link and image in the built pages is checked.

    python3 tools/build.py          build and check
    python3 tools/build.py --check  only check that the built pages are up to date and their links resolve

A page starts with a comment of settings:

    <!--
    title: Download
    description: One sentence for search results and link previews.
    nav: download        (which header link is the current page; optional)
    script: yes          (load assets/site.js, for pages that read the update site; optional)
    gallery: yes         (load assets/gallery.js, the walk down the corridor; optional)
    -->

The six modules are in src/modules.json. Each gets a room, apps/<slug>/, from src/partials/room.html, and pages can
place {{gallery}} (the corridor's framed pieces) and {{rooms}} (a plain list of the rooms).
"""
import hashlib
import html
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SITE = "https://www.fullcompass.co.uk"


def settings(text, name):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    if not m:
        sys.exit(f"{name}: no settings comment at the top")
    values = {}
    for line in m.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        values[key.strip()] = value.split("  (")[0].strip()
    for key in ("title", "description"):
        if not values.get(key):
            sys.exit(f"{name}: no {key}")
    return values, text[m.end():]


def target(name):
    """The built file and the page's address."""
    stem = name[:-5]
    if stem == "index":
        return ROOT / "index.html", "/"
    if stem == "404":
        return ROOT / "404.html", "/404.html"
    return ROOT / stem / "index.html", f"/{stem}/"


def stamp(asset):
    """A few characters of the file's hash, so a changed stylesheet or script is fetched afresh."""
    return hashlib.sha256((ROOT / "assets" / asset).read_bytes()).hexdigest()[:8]


def esc(s):
    return html.escape(s, quote=True)


def modules():
    return json.loads((SRC / "modules.json").read_text())


def gallery_pieces(mods):
    """The corridor's pieces: odd numbers hang on the left, even on the right."""
    out = []
    for i, m in enumerate(mods):
        side = "left" if i % 2 == 0 else "right"
        out.append(
            f'<li class="piece {side}" id="room-{i + 1}" style="--i:{i}" data-name="{esc(m["name"])}" data-kind="{esc(m["kind"])}">\n'
            f'  <a href="/apps/{m["slug"]}/">\n'
            f'    <span class="frame" style="view-transition-name: art-{m["slug"]}"><img src="/assets/img/gallery/{m["art"]}.svg" width="600" height="800" alt="&ldquo;{esc(m["piece"])}&rdquo;, the artwork for {esc(m["name"])}."></span>\n'
            f'    <span class="plaque"><span class="num">{i + 1:02d}</span><span class="kind">{esc(m["kind"])}</span>'
            f'<strong>{esc(m["name"])}</strong><span class="line">{esc(m["line"])}</span><span class="enter">Enter the room</span></span>\n'
            f'  </a>\n</li>')
    return "\n".join(out)


def room_list(mods):
    out = []
    for i, m in enumerate(mods):
        out.append(
            f'<li><a class="room-row" href="/apps/{m["slug"]}/">'
            f'<span class="num">{i + 1:02d}</span>'
            f'<img src="/assets/img/gallery/{m["art"]}.svg" width="600" height="800" alt="">'
            f'<span><span class="kind">{esc(m["kind"])}</span><strong>{esc(m["name"])}</strong><span class="line">{esc(m["summary"])}</span></span>'
            f'</a></li>')
    return "\n".join(out)


def room_pages(mods):
    """A page of source for each module's room, from src/partials/room.html."""
    template = (SRC / "partials" / "room.html").read_text()
    pages = {}
    for i, m in enumerate(mods):
        prev, nxt = mods[i - 1], mods[(i + 1) % len(mods)]
        points = "\n".join(f'      <li><h3>{esc(h)}</h3><p>{esc(p)}</p></li>' for h, p in m["points"])
        fields = {
            "num": f"{i + 1:02d}", "n": str(i + 1), "slug": m["slug"], "art": m["art"], "piece": esc(m["piece"]), "kind": esc(m["kind"]),
            "name": esc(m["name"]), "summary": esc(m["summary"]), "links": esc(m["links"]), "points": points,
            "prev_slug": prev["slug"], "prev_name": esc(prev["short"]), "prev_num": f"{(i - 1) % len(mods) + 1:02d}",
            "next_slug": nxt["slug"], "next_name": esc(nxt["short"]), "next_num": f"{(i + 1) % len(mods) + 1:02d}",
        }
        text = template
        for key, value in fields.items():
            text = text.replace("{{" + key + "}}", value)
        pages[f"apps/{m['slug']}.html"] = text
    return pages


def build():
    head = (SRC / "partials" / "head.html").read_text()
    header = (SRC / "partials" / "header.html").read_text()
    footer = (SRC / "partials" / "footer.html").read_text()
    built = {}
    mods = modules()
    sources = {page.name: page.read_text() for page in sorted((SRC / "pages").glob("*.html"))}
    sources.update(room_pages(mods))
    for name, source in sources.items():
        source = source.replace("{{gallery}}", gallery_pieces(mods)).replace("{{rooms}}", room_list(mods))
        values, body = settings(source, name)
        out, path = target(name)
        title = values["title"]
        full_title = "Full Compass Accountancy Suite" if name == "index.html" else f"{title} | Full Compass Accountancy Suite"
        h = head.replace("{{title}}", html.escape(full_title)).replace("{{description}}", html.escape(values["description"]))
        h = h.replace("{{url}}", SITE + path)
        scripts = [f'<script src="/assets/{file}.js" defer></script>' for key, file in (("script", "site"), ("gallery", "gallery")) if values.get(key) == "yes"]
        if scripts:
            h = h.replace("{{script}}", "\n".join(scripts))
        else:
            h = h.replace("{{script}}\n", "").replace("{{script}}", "")
        nav = header
        current = values.get("nav")
        if current:
            nav = nav.replace(f'data-nav="{current}"', 'aria-current="page"')
        nav = re.sub(r' data-nav="[a-z-]+"', "", nav)
        for asset in ("site.css", "site.js", "gallery.js"):
            h = h.replace(f'/assets/{asset}"', f'/assets/{asset}?v={stamp(asset)}"')
        text = "<!doctype html>\n" + '<html lang="en-GB">\n' + h + "<body>\n" + nav + body.strip() + "\n" + footer + "</body>\n</html>\n"
        built[out] = text
    return built


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if a.get("srcset"):
            self.refs += [part.strip().split(" ")[0] for part in a["srcset"].split(",")]


def check(built):
    problems = []
    pages = {}
    for out, text in built.items():
        p = Links()
        p.feed(text)
        pages[out] = p
    for out, p in pages.items():
        for ref in p.refs:
            if re.match(r"^(https?:|mailto:|#$)", ref):
                continue
            path, _, frag = ref.partition("#")
            path = path.partition("?")[0]
            if not path:
                if frag and frag not in p.ids:
                    problems.append(f"{out.relative_to(ROOT)}: no #{frag} on the page")
                continue
            if not path.startswith("/"):
                problems.append(f"{out.relative_to(ROOT)}: relative link {ref} (use a path from the site's root)")
                continue
            file = ROOT / path.lstrip("/")
            if path.endswith("/"):
                file = file / "index.html"
            if not file.exists() and file not in built:
                problems.append(f"{out.relative_to(ROOT)}: {ref} does not exist")
            elif frag and file in pages and frag not in pages[file].ids:
                problems.append(f"{out.relative_to(ROOT)}: {ref}: no #{frag} there")
    return problems


def main():
    built = build()
    if "--check" in sys.argv:
        stale = [str(o.relative_to(ROOT)) for o, t in built.items() if not o.exists() or o.read_text() != t]
        if stale:
            sys.exit("Out of date (run python3 tools/build.py): " + ", ".join(stale))
    else:
        for out, text in built.items():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text)
        print(f"Built {len(built)} pages.")
    problems = check(built)
    if problems:
        sys.exit("\n".join(problems))
    print("Links and images all resolve.")


if __name__ == "__main__":
    main()
