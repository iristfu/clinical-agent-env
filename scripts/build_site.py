"""Build site/index.html from WRITEUP.md, so the writeup can be read as a web page.

  python scripts/build_site.py           # rebuild site/index.html
  python scripts/build_site.py --check   # exit 1 if site/index.html is out of date (used by the test suite)

WRITEUP.md stays the source of truth. The .githooks/pre-commit hook runs this whenever WRITEUP.md is committed and
stages the result, and tests/test_site.py fails if the two ever drift. site/ is a plain static folder (index.html plus
style.css), so any static host can serve it; vercel.json points Vercel at it.

Needs pandoc on PATH (https://pandoc.org/installing.html).
"""

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "WRITEUP.md"
OUT = ROOT / "site" / "index.html"

TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Clinical agent environment for Opus 5: tasks, graders, calibration and results.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="style.css">
</head><body>
<div class="page">
<nav class="rail" aria-label="Contents"><h2>Contents</h2><ol>{toc}</ol></nav>
<main>
<header class="top"><h1>{title}</h1></header>
{body}
</main>
</div>
</body></html>
"""


def render():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is not installed; see https://pandoc.org/installing.html")
    md = SOURCE.read_text()
    title_match = re.match(r"#\s+(.+)\n", md)
    title = title_match.group(1).strip() if title_match else "Writeup"
    md = md[title_match.end():] if title_match else md
    # The link back to this page is only useful in the markdown, so drop it from the HTML.
    md = re.sub(r"^> \*\*Read this as a web page:\*\*.*\n\n?", "", md, flags=re.M)
    body = subprocess.run(["pandoc", "-f", "markdown", "-t", "html5", "--wrap=none"], input=md, text=True,
                          capture_output=True, check=True).stdout
    body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    toc = "".join(f'<li><a href="#{m.group(1)}">{m.group(2)}</a></li>'
                  for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body))
    return TEMPLATE.format(title=html.escape(title), toc=toc, body=body.strip())


def main():
    page = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != page:
            sys.exit("site/index.html is out of date: run python scripts/build_site.py")
        return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
