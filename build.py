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
            {k: esc(v) for k, v in s.items()},
            url=SITE + s["path"],
            alternates=alternates,
            og_alternates=og_alts,
            lang_links=links,
        )
        out = ROOT / s["path"].strip("/") / "index.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(page, encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
