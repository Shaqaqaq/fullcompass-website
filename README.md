# www.fullcompass.co.uk

The website of the Full Compass Accountancy Suite: what it is, the six apps, the download, what's new, help,
privacy and contact. Plain HTML and CSS, one small script, served by GitHub Pages.

The installers are not hosted here: the download links go to the suite's update site,
https://updates.fullcompass.co.uk/ (its own repository, `fullcompass-updates`).

## Layout

| Path | What it is |
| --- | --- |
| `src/pages/*.html` | Each page's content, with its title and description in a comment at the top |
| `src/partials/` | The shared `<head>`, header and footer |
| `tools/build.py` | Builds the pages and checks every internal link and image |
| `index.html`, `apps/`, `download/`, `whats-new/`, `help/`, `privacy/`, `contact/`, `404.html` | The built pages GitHub Pages serves (don't edit these: edit `src/` and build) |
| `assets/site.css` | The one stylesheet: light and dark by the visitor's system setting |
| `assets/site.js` | Reads `https://updates.fullcompass.co.uk/updates.json` (the signed list the start page reads) for the setup's version, size, SHA-256 and link, and each app's release notes. The pages keep a written fallback if it can't be read |
| `assets/img/` | The compass mark (drawn in VectorCraft), the sharing card and the apps' icons |
| `design/` | The VectorCraft documents for the mark and the sharing card |
| `CNAME` | `www.fullcompass.co.uk`, for GitHub Pages |

## Building and previewing

```
python3 tools/build.py                 # after editing anything in src/
python3 tools/build.py --check         # built pages up to date, links all resolve
python3 -m http.server 1650            # then open http://localhost:1650/
```

## Images

- The mark (`assets/img/mark.svg`, the favicon and touch icons) and the sharing card (`sharing-card.png`, 1200 x 630)
  were drawn in VectorCraft through its control channel; the sources are in `design/`.
- The apps' icons come from the suite's own app icons, resized in PhotoCraft.

## Rules

- No real client, employee or taxpayer data, anywhere.
- Never name other accountancy software, or describe Full Compass as a copy of anything.
- Claim no HMRC or Companies House recognition, accreditation or approval. Describe filing only as far as it is built
  and tested; the suite's docs say how far that is.
- Commits use the GitHub no-reply address.

## Hosting

GitHub Pages from the `main` branch, custom domain `www.fullcompass.co.uk` (the `CNAME` file), with Enforce HTTPS on
once GitHub has issued the certificate. At Namecheap (the domain's DNS):

| Type | Host | Value |
| --- | --- | --- |
| A | `@` | 185.199.108.153 |
| A | `@` | 185.199.109.153 |
| A | `@` | 185.199.110.153 |
| A | `@` | 185.199.111.153 |
| CNAME | `www` | `shaqaqaq.github.io.` |

The bare domain's A records send fullcompass.co.uk to GitHub Pages, which redirects it to www. The mail records
(MX `mx1`/`mx2.privateemail.com` and the mail TXT/SPF records) stay exactly as they are, and so does the `updates`
CNAME of the update site.
