---
name: compile-notes
description: Compile all note PDFs in the MyNotes folder into a single searchable notes_compiled.pdf with a bookmarks sidebar - one chapter per sub-folder, one section per PDF. Use when the user asks to compile, merge, combine, rebuild or refresh their notes PDF.
---

# Compile notes

Builds `MyNotes/notes_compiled.pdf` from every PDF in the sub-folders of `MyNotes`.

## Structure of the output

- **Contents page** listing every chapter and section with page numbers.
- **Chapters** = sub-folders of `MyNotes`, sorted by name (e.g. `Geology`, `Geostatistics`, `Mining`). Each starts with a divider page.
- **Sections** = the PDFs inside each folder, sorted by file name; the section title is the file name without `.pdf`.
- **Bookmarks (outline)** nested as chapter > section. The file opens with the bookmarks sidebar shown, so readers can jump between chapters and sections.
- **Searchable**: source pages are copied as-is, so their text stays selectable and searchable. (A source PDF that is only a scanned image will not be searchable.)

Hidden folders (`.claude`, `.venv`, ...), loose PDFs directly in `MyNotes`, and `notes_compiled.pdf` itself are skipped.

## How to run

The script needs `pypdf` and `reportlab`. Use a virtual environment in `MyNotes/.venv` (create it once if missing):

```bash
cd "<path to>/MyNotes"
[ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -q pypdf reportlab)
.venv/bin/python .claude/skills/compile-notes/compile_notes.py
```

Options:

- `ROOT` positional argument - a different notes folder (default: the `MyNotes` folder that contains this skill).
- `-o PATH` - a different output file (default: `ROOT/notes_compiled.pdf`).
- `--title "..."` - the title on the contents page (default: `My Notes`).

## Steps for Claude

1. Run the commands above from the `MyNotes` folder. If `.venv` is missing, create it as shown.
2. Report the summary line the script prints (chapters, sections, pages, and counts per folder).
3. If the script reports no PDFs, check the folder layout with `ls` and tell the user.
4. Do not commit `notes_compiled.pdf` or `.venv` unless the user asks.
