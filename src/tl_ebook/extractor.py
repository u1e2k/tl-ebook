"""
Extractor module: Extracts structured text (chapters, sections, paragraphs)
from source PDF and EPUB files with formatting preservation.
"""

from collections import Counter
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import pypdf


@dataclass
class Paragraph:
    id: str
    text: str
    is_heading: bool = False
    heading_level: int = 0


class PdfExtractor:
    """Extracts structured text from PDF using dynamic relative indentation and outline bookmarks."""

    def __init__(self, pdf_path: Path | str):
        self.pdf_path = Path(pdf_path)
        self.reader = pypdf.PdfReader(str(self.pdf_path))

    def get_toc(self) -> List[Dict[str, Any]]:
        """Extract bookmarks / outline with start page indices."""
        outline = self.reader.outline
        items: List[Dict[str, Any]] = []

        def recurse(nodes, parent_title=None):
            for node in nodes:
                if isinstance(node, list):
                    recurse(node, parent_title)
                else:
                    title = getattr(node, "title", str(node))
                    try:
                        page_num = self.reader.get_destination_page_number(node)
                    except Exception:
                        page_num = None
                    items.append({
                        "title": title,
                        "page": page_num,
                        "parent": parent_title,
                    })

        recurse(outline)
        return items

    def extract_page_lines(self, page_index: int) -> List[Dict[str, Any]]:
        """
        Extract lines on a single page with relative indentation calculation.
        Handles odd/even alternating page margins automatically.
        """
        page = self.reader.pages[page_index]
        runs: List[Dict[str, Any]] = []

        def visitor(text, cm, tm, font_dict, font_size):
            if text.strip():
                runs.append({"x0": tm[4], "y0": tm[5], "text": text})

        page.extract_text(visitor_text=visitor)
        if not runs:
            return []

        # Sort top to bottom: y0 is increasing down the page in this layout
        runs.sort(key=lambda r: (r["y0"], r["x0"]))

        lines: List[Dict[str, Any]] = []
        curr_y = None
        curr_runs = []

        for r in runs:
            if curr_y is None or abs(r["y0"] - curr_y) <= 3.0:
                curr_y = r["y0"]
                curr_runs.append(r)
            else:
                curr_runs.sort(key=lambda item: item["x0"])
                line_text = "".join(item["text"] for item in curr_runs).strip()
                if line_text:
                    lines.append({"x0": curr_runs[0]["x0"], "y0": curr_y, "text": line_text})
                curr_y = r["y0"]
                curr_runs = [r]

        if curr_runs:
            curr_runs.sort(key=lambda item: item["x0"])
            line_text = "".join(item["text"] for item in curr_runs).strip()
            if line_text:
                lines.append({"x0": curr_runs[0]["x0"], "y0": curr_y, "text": line_text})

        # Calculate page base margin dynamically
        x0_counts = Counter(round(l["x0"], 1) for l in lines)
        if x0_counts:
            base_x0 = x0_counts.most_common(1)[0][0]
        else:
            base_x0 = 0.0

        for l in lines:
            l["indent"] = l["x0"] - base_x0

        return lines

    def extract_range_paragraphs(
        self,
        start_page: int,
        end_page: int,
        chapter_prefix: str,
        indent_threshold: float = 10.0,
    ) -> List[Paragraph]:
        """
        Extract clean, hyphen-reconstructed paragraphs across a page range (inclusive).
        Paragraph starts are identified by relative indent >= indent_threshold (typically 16pt).
        """
        paragraphs: List[Paragraph] = []
        cur_p = ""
        p_index = 1

        for p_idx in range(start_page, end_page + 1):
            if p_idx >= len(self.reader.pages):
                break
            lines = self.extract_page_lines(p_idx)
            for line in lines:
                t = line["text"]
                indent = line.get("indent", 0.0)

                # Skip header/footer artifacts
                if re.match(r"^\d+$", t):
                    continue
                if t.lower() in [
                    "visual thinking",
                    "temple grandin",
                    "introduction",
                ]:
                    continue

                if indent >= indent_threshold:
                    if cur_p:
                        paragraphs.append(
                            Paragraph(
                                id=f"{chapter_prefix}_p{p_index:02d}",
                                text=cur_p.strip(),
                            )
                        )
                        p_index += 1
                    cur_p = t
                else:
                    if cur_p:
                        if cur_p.endswith("-"):
                            cur_p = cur_p[:-1] + t
                        else:
                            cur_p += " " + t
                    else:
                        cur_p = t

        if cur_p:
            paragraphs.append(
                Paragraph(
                    id=f"{chapter_prefix}_p{p_index:02d}",
                    text=cur_p.strip(),
                )
            )

        return paragraphs

    def save_chapter_json(self, paragraphs: List[Paragraph], output_path: Path | str):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [{"id": p.id, "en": p.text} for p in paragraphs]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
