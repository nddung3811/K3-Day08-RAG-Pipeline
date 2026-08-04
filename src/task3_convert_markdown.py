"""
Task 3 - Convert files in data/landing/ to Markdown.

The lab recommends MarkItDown. This implementation uses MarkItDown when it is
installed, and falls back to stdlib converters for DOCX/JSON/HTML so the lab can
run in a fresh environment.
"""

import html
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _docx_to_text(filepath: Path) -> str:
    """Extract readable text from a DOCX file using only Python stdlib."""
    with zipfile.ZipFile(filepath) as docx:
        xml_content = docx.read("word/document.xml")

    root = ET.fromstring(xml_content)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        if texts:
            paragraphs.append("".join(texts))
    return "\n\n".join(paragraphs)


def _html_to_markdown(filepath: Path) -> str:
    raw = filepath.read_text(encoding="utf-8")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", raw)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = re.sub(r"(?i)</h[1-6]\s*>", "\n\n", text)
    text = re.sub(r"(?s)<[^>]+>", "", text)
    return html.unescape(text).strip()


def _pdf_to_text(filepath: Path) -> str:
    """Extract text from a PDF with pypdf when MarkItDown is unavailable."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            f"Cannot convert {filepath.name}. Install markitdown[pdf] or pypdf."
        ) from exc

    reader = PdfReader(str(filepath))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"## Page {index}\n\n{page_text.strip()}")
    return "\n\n".join(pages)


def _convert_document(filepath: Path) -> str:
    if MarkItDown is not None:
        return MarkItDown().convert(str(filepath)).text_content

    suffix = filepath.suffix.lower()
    if suffix == ".pdf":
        return _pdf_to_text(filepath)
    if suffix == ".docx":
        return _docx_to_text(filepath)
    if suffix in (".html", ".htm"):
        return _html_to_markdown(filepath)
    if suffix in (".md", ".txt"):
        return filepath.read_text(encoding="utf-8")

    raise RuntimeError(f"Cannot convert unsupported file type: {filepath.name}")


def convert_legal_docs():
    """Convert PDF/DOCX files in data/landing/legal/ to markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc", ".html", ".htm", ".md", ".txt"):
            print(f"Converting: {filepath.name}")
            text_content = _convert_document(filepath)
            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(text_content, encoding="utf-8")
            print(f"  Saved: {output_path}")


def convert_news_articles():
    """Convert JSON/HTML crawled articles in data/landing/news/ to markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"  Saved: {output_path}")
        elif filepath.suffix.lower() in (".html", ".htm"):
            print(f"Converting: {filepath.name}")
            output_path = output_dir / f"{filepath.stem}.md"
            output_path.write_text(_html_to_markdown(filepath), encoding="utf-8")
            print(f"  Saved: {output_path}")


def convert_all():
    """Run the full conversion step."""
    print("=" * 50)
    print("Task 3: Convert to Markdown")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\nDone! Output:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
