#!/usr/bin/env python3
"""
export.py -- convert a composed CV or cover letter (Markdown) to PDF.

Usage:
    python export.py <markdown_file> <cv|cl> [--paper A4|Letter]

Pipeline:
    1. Read the Markdown file and strip YAML front matter.
    2. Convert to HTML with Pandoc.
    3. Inject the CSS template (cv.css or cl.css, next to this script).
    4. Render to PDF with a headless Chromium-based browser
       (Chrome, Edge, Chromium or Brave).
    5. Write the PDF next to the input, same name, .pdf extension.

Needs:
    pandoc            https://pandoc.org/installing.html
    a Chromium-based browser. Set CAREER_BROWSER to its full path if it is
    installed somewhere unusual.

Standard library only.
"""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


BROWSER_NAMES = [
    "google-chrome",
    "google-chrome-stable",
    "chrome",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "microsoft-edge-stable",
    "msedge",
    "brave-browser",
]


def _windows_candidates():
    roots = [
        os.environ.get("PROGRAMFILES", r"C:\Program Files"),
        os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),
    ]
    rel = [
        r"Google\Chrome\Application\chrome.exe",
        r"Microsoft\Edge\Application\msedge.exe",
        r"Chromium\Application\chrome.exe",
        r"BraveSoftware\Brave-Browser\Application\brave.exe",
    ]
    return [str(Path(root) / r) for root in roots if root for r in rel]


def _macos_candidates():
    apps = [
        "Google Chrome.app/Contents/MacOS/Google Chrome",
        "Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "Chromium.app/Contents/MacOS/Chromium",
        "Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    roots = ["/Applications", str(Path.home() / "Applications")]
    return [str(Path(root) / a) for root in roots for a in apps]


def _linux_candidates():
    return [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        "/snap/bin/chromium",
    ]


def find_browser() -> str:
    """Return the path of a Chromium-based browser, or exit with a clear message."""
    override = os.environ.get("CAREER_BROWSER", "").strip()
    if override:
        if Path(override).exists():
            return override
        fail(f"CAREER_BROWSER is set to {override}, but that file does not exist.")

    system = platform.system()
    if system == "Windows":
        candidates = _windows_candidates()
    elif system == "Darwin":
        candidates = _macos_candidates()
    else:
        candidates = _linux_candidates()

    for path in candidates:
        if Path(path).exists():
            return path
    for name in BROWSER_NAMES:
        found = shutil.which(name)
        if found:
            return found

    fail(
        "No Chromium-based browser found (looked for Chrome, Edge, Chromium and Brave).\n"
        "Install one, or set CAREER_BROWSER to the full path of its executable."
    )


def find_pandoc() -> str:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        fail(
            "pandoc is not installed or not on PATH.\n"
            "Install it from https://pandoc.org/installing.html and try again."
        )
    return pandoc


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def strip_frontmatter(markdown: str) -> str:
    """Remove YAML front matter delimited by --- ... ---"""
    pattern = r"^---\s*\n.*?\n---\s*\n"
    return re.sub(pattern, "", markdown, count=1, flags=re.DOTALL)


def md_to_html(markdown_text: str, pandoc: str) -> str:
    """Convert Markdown to standalone HTML with Pandoc."""
    try:
        result = subprocess.run(
            [pandoc, "--from=markdown-smart", "--to=html5", "--standalone",
             "--metadata", "pagetitle=document"],
            input=markdown_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except FileNotFoundError:
        fail("pandoc could not be started. Check that it is installed and on PATH.")
    if result.returncode != 0:
        fail(f"Pandoc failed:\n{result.stderr}")
    return result.stdout


def post_process_html(html: str) -> str:
    """Restructure Pandoc HTML for CV rendering.

    Pandoc merges the contact, links and languages lines under the name into
    one <p>. Split it into classed <div>s, and split the metadata paragraph
    under each role heading into organisation and date lines.
    """
    def split_contact_block(match):
        raw = match.group(1)
        content = re.sub(r"\s+", " ", raw).strip()

        # Contact line: everything up to the first link
        link_start = re.search(r"<a\s", content)
        if not link_start:
            return match.group(0)

        contact = content[:link_start.start()].rstrip(" |")
        rest = content[link_start.start():]

        # Language line after the last link, e.g. "English (Native) | Spanish (Fluent)"
        lang_match = re.search(
            r"</a>\s*(\|?\s*)([A-Z][a-z]+\s*\([^)]+\)(?:\s*\|\s*[A-Z][a-z]+\s*\([^)]+\))*)\s*$",
            rest,
        )
        if lang_match:
            links = rest[:lang_match.start() + len("</a>")].strip().rstrip(" |")
            lang = lang_match.group(2).strip()
            return (f'<div class="contact-line">{contact}</div>\n'
                    f'<div class="contact-links">{links}</div>\n'
                    f'<div class="contact-lang">{lang}</div>')
        return (f'<div class="contact-line">{contact}</div>\n'
                f'<div class="contact-links">{rest}</div>')

    html = re.sub(
        r"</h1>\s*<p>(.*?)</p>",
        lambda m: "</h1>\n" + split_contact_block(m),
        html,
        count=1,
        flags=re.DOTALL,
    )

    # After each h3 (role or project), a <p> holding an optional <em>org</em>
    # then the dates and scope. Split into .role-org and .role-meta.
    def split_role_meta(match):
        h3 = match.group(1)
        para = re.sub(r"\s+", " ", match.group(2)).strip()
        em_match = re.match(r"<em>(.*?)</em>\s*(.*)", para)
        if em_match:
            org = em_match.group(1).strip()
            meta = em_match.group(2).strip()
            return (f"{h3}\n"
                    f'<div class="role-org">{org}</div>\n'
                    f'<div class="role-meta">{meta}</div>')
        return f'{h3}\n<div class="role-meta">{para}</div>'

    html = re.sub(
        r"(<h3[^>]*>.*?</h3>)\s*<p>(.*?)</p>",
        split_role_meta,
        html,
        flags=re.DOTALL,
    )
    return html


def inject_css(html: str, css_path: Path, paper: str) -> str:
    """Replace Pandoc's default style block with the template CSS."""
    css_content = css_path.read_text(encoding="utf-8")
    css_content = re.sub(r"size:\s*A4\s*;", f"size: {paper};", css_content)
    style_tag = f"<style>\n{css_content}\n</style>"
    if "<style>" in html:
        html = re.sub(r"<style>.*?</style>", lambda m: style_tag, html, count=1, flags=re.DOTALL)
    elif "</head>" in html:
        html = html.replace("</head>", f"{style_tag}\n</head>")
    return html


def render_pdf(html: str, output_path: Path, browser: str) -> None:
    """Render HTML to PDF with the headless browser."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tmp_html = f.name

    try:
        try:
            result = subprocess.run(
                [
                    browser,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-extensions",
                    "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={output_path}",
                    "--no-pdf-header-footer",
                    Path(tmp_html).as_uri(),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except FileNotFoundError:
            fail(f"The browser at {browser} could not be started.")
        except subprocess.TimeoutExpired:
            fail("The browser took longer than 60 seconds to render the PDF.")
        if not output_path.exists():
            fail(f"The browser did not produce a PDF (exit code {result.returncode}):\n{result.stderr}")
    finally:
        Path(tmp_html).unlink(missing_ok=True)


def get_page_count(pdf_path: Path) -> int:
    """Count page objects in the PDF."""
    try:
        content = pdf_path.read_bytes()
        pages = len(re.findall(rb"/Type\s*/Page(?!s)", content))
        return max(pages, 1)
    except OSError:
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a composed CV or cover letter from Markdown to PDF.")
    parser.add_argument("markdown_file", help="the composition .md file")
    parser.add_argument("template", choices=["cv", "cl"], help="cv or cl (cover letter)")
    parser.add_argument("--paper", choices=["A4", "Letter"], default="A4",
                        help="paper size; use the profile's settings.paper (default A4)")
    args = parser.parse_args()

    md_path = Path(args.markdown_file).resolve()
    if not md_path.exists():
        fail(f"File not found: {md_path}")

    css_path = Path(__file__).resolve().parent / f"{args.template}.css"
    if not css_path.exists():
        fail(f"CSS template not found: {css_path}")

    # Check both external tools before doing any work.
    pandoc = find_pandoc()
    browser = find_browser()

    print(f"Reading: {md_path.name}")
    markdown = strip_frontmatter(md_path.read_text(encoding="utf-8"))

    print("Converting to HTML with Pandoc...")
    html = md_to_html(markdown, pandoc)
    if args.template == "cv":
        html = post_process_html(html)
    html = inject_css(html, css_path, args.paper)

    output_path = md_path.with_suffix(".pdf")
    print(f"Rendering PDF with {Path(browser).name}...")
    render_pdf(html, output_path, browser)

    pages = get_page_count(output_path)
    size_kb = output_path.stat().st_size / 1024
    print(f"OK: {output_path.name} ({pages} page{'s' if pages != 1 else ''}, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
