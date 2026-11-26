"""Render index.html (English, site root) and it/index.html from template.html + strings.json.

Usage: python3 build.py
"""
import html
import json
from pathlib import Path
from string import Template

ROOT = Path(__file__).parent
SITE = "https://katiedepaoli.com"


def esc(s):
    return html.escape(s, quote=False).replace('"', "&quot;")


def stats(items):
    return "\n".join(
        f'      <li><span class="n">{esc(i["n"])}</span><span class="t">{esc(i["t"])}</span></li>' for i in items
    )


def what(items):
    return "\n".join(
        f'      <li><h3>{esc(i["h"])}</h3><p>{esc(i["p"])}</p></li>' for i in items
    )


def jobs(items):
    out = []
    for j in items:
        roles = "\n".join(
            f'          <li><span class="rt">{esc(r["title"])}</span><span class="rd">{esc(r["dates"])}</span>'
            + (f'<span class="rn">{esc(r["note"])}</span>' if r.get("note") else "")
            + "</li>"
            for r in j["roles"]
        )
        points = "".join(f"\n          <li>{esc(p)}</li>" for p in j["points"])
        out.append(
            f'      <article class="job">\n'
            f'        <h3>{esc(j["org"])}</h3>\n'
            f'        <p class="jm">{esc(j["meta"])}</p>\n'
            f'        <ul class="roles">\n{roles}\n        </ul>\n'
            + (f'        <ul class="points">{points}\n        </ul>\n' if points else "")
            + "      </article>"
        )
    return "\n".join(out)


def main():
    langs = json.loads((ROOT / "strings.json").read_text(encoding="utf-8"))
    tpl = Template((ROOT / "template.html").read_text(encoding="utf-8"))

    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{s["lang"]}" href="{SITE}{s["path"]}">' for s in langs.values()
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'

    for s in langs.values():
        links = "\n".join(
            f'    <a href="{o["path"]}" lang="{o["lang"]}" hreflang="{o["lang"]}"'
            + (' aria-current="page"' if o is s else "")
            + f'>{esc(o["native"])}</a>'
            for o in langs.values()
        )
        og_alts = "\n".join(
            f'<meta property="og:locale:alternate" content="{o["og_locale"]}">'
            for o in langs.values() if o is not s
        )
        page = tpl.substitute(
            {k: esc(v) for k, v in s.items() if isinstance(v, str)},
            url=SITE + s["path"],
            alternates=alternates,
            og_alternates=og_alts,
            lang_links=links,
            stats_html=stats(s["stats"]),
            what_html=what(s["what"]),
            jobs_html=jobs(s["jobs"]),
            how_html="\n".join(f"      <li>{esc(h)}</li>" for h in s["how"]),
            edu_html="\n".join(f"      <li>{esc(e)}</li>" for e in s["edu"]),
        )
        out = ROOT / s["path"].strip("/") / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
