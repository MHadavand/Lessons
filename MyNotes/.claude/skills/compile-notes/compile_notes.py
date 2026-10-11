"""Compile every PDF under the notes root into one bookmarked, searchable PDF.

usage: python compile_notes.py [NOTES_ROOT] [-o OUTPUT]

- Each sub-folder of NOTES_ROOT becomes a chapter (sorted by name).
- Each PDF inside a folder becomes a section (sorted by file name, title = file stem).
- A cover/contents page and a divider page per chapter are generated.
- The output opens with the bookmarks (outline) sidebar visible; text stays searchable
  as long as the source PDFs contain real text.
"""
import argparse
import io
import sys
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import Fit
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUTPUT_NAME = "notes_compiled.pdf"
ACCENT = colors.HexColor("#c0561b")


def discover(root: Path, output: Path):
    chapters = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        pdfs = sorted(
            (p for p in folder.glob("*.pdf") if p.resolve() != output.resolve()),
            key=lambda p: p.stem.lower(),
        )
        if pdfs:
            chapters.append((folder.name, pdfs))
    return chapters


def page_pdf(draw) -> PdfReader:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    draw(c)
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf)


def cover_pages(title, chapters, page_numbers):
    """Contents page(s): chapter and section names with their page numbers.

    Returns the rendered pages and a list of (cover_page_index, rect, target_page) link
    areas, one per contents line; target_page is 1-based in the final document.
    """
    w, h = letter
    lines = []
    for num, (name, pdfs) in enumerate(chapters, 1):
        lines.append(("chapter", f"{num}. {name}", page_numbers[name][0]))
        for pdf in pdfs:
            lines.append(("section", pdf.stem, page_numbers[name][1][pdf]))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    y = h - 1.2 * inch
    c.setFont("Helvetica-Bold", 26)
    c.drawString(inch, y, title)
    y -= 0.35 * inch
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    total = sum(len(p) for _, p in chapters)
    c.drawString(inch, y, f"{len(chapters)} chapters, {total} sections - compiled {date.today().isoformat()}")
    c.setFillColor(colors.black)
    y -= 0.5 * inch
    links, cover_page = [], 0
    for kind, text, page in lines:
        if y < inch:
            c.showPage()
            cover_page += 1
            y = h - inch
        if kind == "chapter":
            y -= 0.12 * inch
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(ACCENT)
            indent = inch
        else:
            c.setFont("Helvetica", 10.5)
            c.setFillColor(colors.black)
            indent = inch + 0.3 * inch
        c.drawString(indent, y, text[:80])
        c.drawRightString(w - inch, y, str(page))
        # Clickable area spanning the whole line, from the title to the page number.
        links.append((cover_page, (indent - 2, y - 4, w - inch + 2, y + 12), page))
        y -= 0.24 * inch if kind == "section" else 0.3 * inch
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf), links


def divider(num, name, pdfs):
    w, h = letter

    def draw(c):
        c.setFillColor(ACCENT)
        c.setFont("Helvetica", 14)
        c.drawString(inch, h / 2 + 0.9 * inch, f"Chapter {num}")
        c.setFont("Helvetica-Bold", 34)
        c.drawString(inch, h / 2 + 0.3 * inch, name)
        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 11)
        c.drawString(inch, h / 2 - 0.1 * inch, f"{len(pdfs)} sections")

    return page_pdf(draw)


def compile_notes(root: Path, output: Path, title: str) -> int:
    chapters = discover(root, output)
    if not chapters:
        print(f"No PDFs found in sub-folders of {root}", file=sys.stderr)
        return 1

    readers = {pdf: PdfReader(str(pdf)) for _, pdfs in chapters for pdf in pdfs}

    # Pass 1: lay out page numbers (1-based) so the contents page can list them.
    def layout(n_cover):
        numbers, page = {}, n_cover + 1
        for name, pdfs in chapters:
            chapter_page, sections = page, {}
            page += 1  # divider
            for pdf in pdfs:
                sections[pdf] = page
                page += len(readers[pdf].pages)
            numbers[name] = (chapter_page, sections)
        return numbers

    n_cover = 1
    while True:  # contents may spill onto extra pages; re-layout until stable
        numbers = layout(n_cover)
        cover, links = cover_pages(title, chapters, numbers)
        if len(cover.pages) == n_cover:
            break
        n_cover = len(cover.pages)

    # Pass 2: assemble and add the nested outline.
    writer = PdfWriter()
    for p in cover.pages:
        writer.add_page(p)
    contents_bm = writer.add_outline_item("Contents", 0, fit=Fit.fit())
    for num, (name, pdfs) in enumerate(chapters, 1):
        start = len(writer.pages)
        writer.add_page(divider(num, name, pdfs).pages[0])
        chapter_bm = writer.add_outline_item(f"{num}. {name}", start, fit=Fit.fit())
        for pdf in pdfs:
            first = len(writer.pages)
            for p in readers[pdf].pages:
                writer.add_page(p)
            writer.add_outline_item(pdf.stem, first, parent=chapter_bm, fit=Fit.fit())

    # Make every contents line a link to its chapter/section page.
    for cover_page, rect, target in links:
        writer.add_annotation(cover_page, Link(rect=rect, target_page_index=target - 1, fit=Fit.fit()))

    writer.add_metadata({"/Title": title, "/Subject": "Compiled notes"})
    writer.page_mode = "/UseOutlines"  # open with the bookmarks sidebar
    del contents_bm
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as f:
        writer.write(f)

    total = sum(len(p) for _, p in chapters)
    print(f"Wrote {output} - {len(chapters)} chapters, {total} sections, {len(writer.pages)} pages")
    for name, pdfs in chapters:
        print(f"  {name}: {len(pdfs)}")
    return 0


def main():
    default_root = Path(__file__).resolve().parents[3]  # MyNotes/.claude/skills/compile-notes -> MyNotes
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", type=Path, default=default_root, help="notes folder (default: MyNotes)")
    ap.add_argument("-o", "--output", type=Path, help=f"output path (default: ROOT/{OUTPUT_NAME})")
    ap.add_argument("--title", default="My Notes", help="title on the contents page")
    args = ap.parse_args()
    root = args.root.resolve()
    output = (args.output or root / OUTPUT_NAME).resolve()
    sys.exit(compile_notes(root, output, args.title))


if __name__ == "__main__":
    main()
