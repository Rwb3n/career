#!/usr/bin/env python3
"""
generate_docx.py -- Convert a composed CV or cover-letter markdown file into an
ATS-optimised .docx.

This is a generic, parametrised generator. It is NOT hardcoded to any candidate.
It reads a markdown file produced by the compose-cv / compose-cover-letter skills
and renders it to Word with ATS-safe formatting:

  - Single column, no tables / text boxes / images
  - Calibri throughout (body 10.5pt, name 20pt, H1 12pt, H2 11pt)
  - Native Word heading styles (so ATS parsers detect structure)
  - Native Word bullet list items (not manual dashes)
  - Contact info in the document body (never headers/footers)

Markdown conventions it understands:
  # Name                -> document title (20pt bold)
  *italic line under name* or a plain line -> headline / contact (body)
  ## Section            -> Heading 1 (Summary, Skills, Experience, ...)
  ### Role Title        -> Heading 2
  - bullet              -> native bullet list item
  plain paragraph       -> body paragraph
  YAML frontmatter (--- ... ---) is skipped.

Usage:
  python generate_docx.py INPUT.md OUTPUT.docx
  python generate_docx.py INPUT.md            # writes alongside input as .docx

Requires: python-docx  (pip install python-docx)
"""

import re
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    sys.stderr.write(
        "ERROR: python-docx is not installed.\n"
        "Install it with:  pip install python-docx\n"
    )
    sys.exit(1)


BODY_FONT = "Calibri"
BODY_SIZE = 10.5
NAME_SIZE = 20
H1_SIZE = 12
H2_SIZE = 11
ACCENT = RGBColor(0x1F, 0x38, 0x64)  # navy; ATS ignores colour, harmless for humans


def strip_frontmatter(text: str) -> str:
    """Remove a leading YAML frontmatter block delimited by --- ... ---."""
    if text.lstrip().startswith("---"):
        # find the closing --- after the opening one
        lines = text.splitlines()
        # locate first ---
        start = next((i for i, l in enumerate(lines) if l.strip() == "---"), None)
        if start is not None:
            end = next(
                (i for i in range(start + 1, len(lines)) if lines[i].strip() == "---"),
                None,
            )
            if end is not None:
                return "\n".join(lines[end + 1 :])
    return text


def clean_inline(text: str) -> str:
    """Strip markdown emphasis and link syntax to plain text (ATS-safe)."""
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 \2", text)  # [label](url) -> label url
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return text.strip()


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_SIZE)

    for style_name, size in (("Heading 1", H1_SIZE), ("Heading 2", H2_SIZE)):
        st = doc.styles[style_name]
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = ACCENT if style_name == "Heading 1" else RGBColor(0, 0, 0)

    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(2.2)
    section.right_margin = Cm(2.2)


def render(md_path: Path, out_path: Path) -> None:
    raw = strip_frontmatter(md_path.read_text(encoding="utf-8"))
    lines = raw.splitlines()

    doc = Document()
    configure_styles(doc)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("# ") and not stripped.startswith("## "):
            # Document title (name)
            p = doc.add_paragraph()
            run = p.add_run(clean_inline(stripped[2:]))
            run.font.size = Pt(NAME_SIZE)
            run.font.bold = True
            run.font.name = BODY_FONT
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif stripped.startswith("### "):
            doc.add_heading(clean_inline(stripped[4:]), level=2)
        elif stripped.startswith("## "):
            doc.add_heading(clean_inline(stripped[3:]), level=1)
        elif stripped.startswith(("- ", "* ")):
            doc.add_paragraph(clean_inline(stripped[2:]), style="List Bullet")
        else:
            # plain paragraph (headline, contact line, summary text, etc.)
            doc.add_paragraph(clean_inline(stripped))

    doc.save(str(out_path))
    print(f"Wrote {out_path}")


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write(__doc__ or "Usage: python generate_docx.py INPUT.md [OUTPUT.docx]\n")
        return 2
    md_path = Path(sys.argv[1])
    if not md_path.exists():
        sys.stderr.write(f"ERROR: input not found: {md_path}\n")
        return 1
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_suffix(".docx")
    render(md_path, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
