"""
Translator module: Manages glossaries, style guides, and translation data representations.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TranslationItem:
    id: str
    en: str
    ja: str = ""
    notes: Optional[str] = None


class TranslationManager:
    """Manages bilingual paragraph structures, glossaries, and exported Markdown."""

    def __init__(self, references_dir: Path | str = "references"):
        self.ref_dir = Path(references_dir)
        self.glossary: Dict[str, str] = {}
        self.load_glossary()

    def load_glossary(self):
        glossary_path = self.ref_dir / "glossary.json"
        if glossary_path.exists():
            try:
                with open(glossary_path, "r", encoding="utf-8") as f:
                    self.glossary = json.load(f)
            except Exception:
                self.glossary = {}

    def load_chapter_en(self, json_path: Path | str) -> List[TranslationItem]:
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [TranslationItem(id=item["id"], en=item["en"]) for item in raw]

    def render_markdown(
        self,
        chapter_title: str,
        items: List[TranslationItem],
        output_path: Path | str,
    ):
        """Render both a fluent Japanese reading text and paragraph-by-paragraph parallel table."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# {chapter_title}\n",
            "---\n",
            "## 日本語訳全文\n",
        ]

        for item in items:
            if item.ja:
                lines.append(f"{item.ja}\n")

        lines.extend([
            "\n---\n",
            "## 日英対訳・段落詳細\n",
        ])

        for item in items:
            lines.append(f"### 段落 [{item.id}]")
            lines.append(f"- **EN**:\n  > {item.en}")
            lines.append(f"- **JA**:\n  > {item.ja or '（未翻訳）'}\n")

        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
