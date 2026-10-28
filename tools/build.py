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
    -->
"""
import html
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


def build():
    head = (SRC / "partials" / "head.html").read_text()
    header = (SRC / "partials" / "header.html").read_text()
    footer = (SRC / "partials" / "footer.html").read_text()
    built = {}
    for page in sorted((SRC / "pages").glob("*.html")):
        values, body = settings(page.read_text(), page.name)
        out, path = target(page.name)
        title = values["title"]
        full_title = "Full Compass Accountancy Suite" if page.name == "index.html" else f"{title} | Full Compass Accountancy Suite"
        h = head.replace("{{title}}", html.escape(full_title)).replace("{{description}}", html.escape(values["description"]))
        h = h.replace("{{url}}", SITE + path)
        if values.get("script") == "yes":
            h = h.replace("{{script}}", '<script src="/assets/site.js" defer></script>')
        else:
            h = h.replace("{{script}}\n", "").replace("{{script}}", "")
        nav = header
        current = values.get("nav")
        if current:
            nav = nav.replace(f'data-nav="{current}"', 'aria-current="page"')
        nav = re.sub(r' data-nav="[a-z-]+"', "", nav)
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
