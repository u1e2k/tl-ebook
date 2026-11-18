"""
Builder module: Compiles translated Markdown chapters into a high-quality EPUB.
"""

from pathlib import Path
import re
from typing import Dict, List, Optional
import ebooklib
from ebooklib import epub


class EpubBuilder:
    """Builds a formatted Japanese EPUB with clean styling and chapter navigation."""

    def __init__(
        self,
        title: str,
        author: str,
        language: str = "ja",
        identifier: Optional[str] = None,
        cover_image_bytes: Optional[bytes] = None,
    ):
        self.book = epub.EpubBook()
        self.book.set_title(title)
        self.book.set_language(language)
        self.book.add_author(author)
        if identifier:
            self.book.set_identifier(identifier)
        else:
            self.book.set_identifier(f"tl-ebook-{title.lower().replace(' ', '-')}")

        if cover_image_bytes:
            self.book.set_cover("cover.jpeg", cover_image_bytes)

        self.chapters: List[epub.EpubHtml] = []
        self._add_default_style()

    def _add_default_style(self):
        style = """
        @charset "UTF-8";
        body {
            font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", "Meiryo", sans-serif;
            line-height: 1.85;
            letter-spacing: 0.03em;
            margin: 5%;
            color: #1a1a1a;
        }
        h1 {
            font-size: 1.6em;
            font-weight: bold;
            border-bottom: 2px solid #333;
            padding-bottom: 0.3em;
            margin-top: 1.5em;
            margin-bottom: 1em;
            page-break-before: always;
        }
        h2 {
            font-size: 1.3em;
            font-weight: bold;
            margin-top: 1.4em;
            margin-bottom: 0.8em;
            color: #2b2b2b;
        }
        h3 {
            font-size: 1.15em;
            font-weight: bold;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
            color: #444;
        }
        p {
            margin-top: 0;
            margin-bottom: 1.2em;
            text-indent: 1em;
            text-align: justify;
        }
        blockquote {
            margin: 1em 1.5em;
            padding: 0.5em 1em;
            border-left: 3px solid #ccc;
            color: #555;
            background-color: #f9f9f9;
        }
        """
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style.encode("utf-8"),
        )
        self.book.add_item(nav_css)

    def add_chapter_from_markdown(
        self,
        file_name: str,
        title: str,
        md_content: str,
        extract_reading_text: bool = True,
    ):
        """
        Parses Markdown and adds it as an EPUB chapter.
        If extract_reading_text is True, extracts the fluent '日本語訳全文' section.
        """
        body_text = md_content
        if extract_reading_text:
            match = re.search(r"## 日本語訳全文\s*(.*?)(?=\n---\n|## 日英対訳|$)", md_content, re.DOTALL)
            if match:
                body_text = match.group(1).strip()

        # Convert simple markdown paragraphs to HTML
        paras = [p.strip() for p in body_text.split("\n\n") if p.strip()]
        html_paras = []
        for p in paras:
            if p.startswith("# "):
                html_paras.append(f"<h1>{p[2:].strip()}</h1>")
            elif p.startswith("## "):
                html_paras.append(f"<h2>{p[3:].strip()}</h2>")
            elif p.startswith("### "):
                html_paras.append(f"<h3>{p[4:].strip()}</h3>")
            else:
                html_paras.append(f"<p>{p}</p>")

        html_content = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="style/nav.css" type="text/css"/>
        </head>
        <body>
            <h1>{title}</h1>
            {''.join(html_paras)}
        </body>
        </html>
        """

        chap = epub.EpubHtml(
            title=title,
            file_name=file_name,
            lang="ja",
        )
        chap.content = html_content.encode("utf-8")
        self.book.add_item(chap)
        self.chapters.append(chap)

    def write_epub(self, output_path: Path | str):
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        self.book.toc = tuple(self.chapters)
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        self.book.spine = ["nav"] + self.chapters
        epub.write_epub(str(out), self.book, {})
