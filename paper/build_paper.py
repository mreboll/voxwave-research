"""Build VoxWave_paper.pdf from voxwave_paper.html with a table of contents whose page numbers
are measured on the rendered PDF (render, locate each heading, fill numbers, re-render until stable).

    ../.venv/Scripts/python.exe build_paper.py
"""
import re
import subprocess
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "voxwave_paper.html"
BUILT_HTML = HERE / "_build.html"
PDF = HERE / "VoxWave_paper.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
FIRST_BODY_PAGE = 2  # the TOC is on page 1; headings are searched from here on
MAX_PASSES = 4


def headings(html: str) -> list[tuple[str, str, str]]:
    """(level, id, text) for every h2/h3 that has an id."""
    out = []
    for level, hid, text in re.findall(r'<(h[23]) id="([^"]+)"[^>]*>(.*?)</\1>', html, flags=re.S):
        out.append((level, hid, re.sub(r"<[^>]+>", "", text).replace("&amp;", "&").strip()))
    return out


def toc_html(items: list[tuple[str, str, str]], pages: dict[str, str]) -> str:
    rows = []
    for level, hid, text in items:
        cls = "l2" if level == "h2" else "l3"
        rows.append(f'<li class="{cls}"><span class="t">{text}</span><span class="dots"></span>'
                    f'<span class="p">{pages.get(hid, "")}</span></li>')
    return '<ol class="toc">' + "".join(rows) + "</ol>"


def render(html: str) -> None:
    BUILT_HTML.write_text(html, encoding="utf-8")
    subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", BUILT_HTML.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def locate(items: list[tuple[str, str, str]]) -> dict[str, str]:
    pages = [norm(p.extract_text() or "") for p in PdfReader(PDF).pages]
    found, start = {}, FIRST_BODY_PAGE - 1
    for _, hid, text in items:
        key = norm(text)[:28]
        for i in range(start, len(pages)):
            if key in pages[i]:
                found[hid] = str(i + 1)
                start = i
                break
    return found


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    items = headings(source)
    pages: dict[str, str] = {}
    for n in range(MAX_PASSES):
        render(source.replace("<!--TOC-->", toc_html(items, pages)))
        new = locate(items)
        if new == pages:
            break
        pages = new
    missing = [t for _, hid, t in items if hid not in pages]
    BUILT_HTML.unlink(missing_ok=True)
    print(f"passes {n + 1}; pages {len(PdfReader(PDF).pages)}; headings {len(items)}; missing {missing}")


if __name__ == "__main__":
    main()
