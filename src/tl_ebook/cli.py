"""
CLI entry point for tl-ebook.
"""

from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from tl_ebook.builder import EpubBuilder
from tl_ebook.colab import ColabBridge
from tl_ebook.extractor import PdfExtractor

console = Console()


@click.group()
def main():
    """tl-ebook: High-fidelity e-book translation pipeline and EPUB builder."""
    pass


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
def toc(pdf_path: str):
    """Display table of contents and page index from source PDF."""
    extractor = PdfExtractor(pdf_path)
    items = extractor.get_toc()

    table = Table(title="Document Outline / Table of Contents")
    table.add_column("Page", justify="right", style="cyan")
    table.add_column("Title", style="green")

    for item in items:
        p = str(item["page"]) if item["page"] is not None else "-"
        indent = "  " if item["parent"] else ""
        table.add_row(p, indent + item["title"])

    console.print(table)


@main.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option(
    "--output-dir",
    "-o",
    default="src_en",
    help="Output directory for extracted JSON files.",
)
def extract(pdf_path: str, output_dir: str):
    """Extract all chapters and sections from PDF into structured JSON."""
    extractor = PdfExtractor(pdf_path)
    toc_items = extractor.get_toc()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Top-level chapters with correct 0-indexed page ranges (end is inclusive)
    chapter_defs = [
        {"prefix": "00_introduction", "title": "Introduction", "start": 8, "end": 14},
        {"prefix": "01_chapter1", "title": "One: What Is Visual Thinking?", "start": 16, "end": 50},
        {"prefix": "02_chapter2", "title": "Two: Screened Out", "start": 52, "end": 83},
        {"prefix": "03_chapter3", "title": "Three: Where Are All the Clever Engineers?", "start": 85, "end": 116},
        {"prefix": "04_chapter4", "title": "Four: Complementary Minds", "start": 118, "end": 147},
        {"prefix": "05_chapter5", "title": "Five: Genius and Neurodiversity", "start": 149, "end": 181},
        {"prefix": "06_chapter6", "title": "Six: Visualizing Risk to Prevent Disasters", "start": 183, "end": 221},
        {"prefix": "07_chapter7", "title": "Seven: Animal Consciousness and Visual Thinking", "start": 223, "end": 256},
        {"prefix": "08_afterword", "title": "Afterword", "start": 258, "end": 261},
        {"prefix": "09_acknowledgments", "title": "Acknowledgments", "start": 262, "end": 262},
    ]

    console.print(f"[bold green]Starting extraction from:[/bold green] {pdf_path}")

    for chap in chapter_defs:
        prefix = chap["prefix"]
        out_file = out_dir / f"{prefix}.json"
        console.print(f"Extracting [cyan]{chap['title']}[/cyan] (pages {chap['start']}-{chap['end']})...")
        paras = extractor.extract_range_paragraphs(
            start_page=chap["start"],
            end_page=chap["end"],
            chapter_prefix=prefix,
        )
        extractor.save_chapter_json(paras, out_file)
        console.print(f"  -> Saved {len(paras)} paragraphs to [yellow]{out_file}[/yellow]")

    console.print("[bold green]Extraction complete![/bold green]")


@main.command()
@click.option(
    "--input-dir",
    "-i",
    default="dist/ja_md",
    help="Directory containing translated Markdown files.",
)
@click.option(
    "--output-epub",
    "-o",
    default="dist/ja_epub/Visual_Thinking_ja.epub",
    help="Output EPUB path.",
)
@click.option("--title", default="ビジュアル・シンカーの脳：見取り図・パターン・抽象で考える人々", help="EPUB book title.")
@click.option("--author", default="テンプル・グランディン, ベッツィ・ラーナー", help="Book author.")
@click.option("--cover", default=None, help="Optional cover image path or source EPUB to extract cover from.")
def build(input_dir: str, output_epub: str, title: str, author: str, cover: str):
    """Build a Japanese EPUB from translated Markdown files."""
    in_dir = Path(input_dir)
    if not in_dir.exists():
        console.print(f"[red]Error: Input directory {input_dir} not found.[/red]")
        return

    md_files = sorted(in_dir.glob("*.md"))
    if not md_files:
        console.print(f"[yellow]Warning: No markdown files found in {input_dir}[/yellow]")
        return

    cover_bytes = None
    if cover:
        cover_path = Path(cover)
        if cover_path.exists():
            if cover_path.suffix.lower() == ".epub":
                import zipfile
                with zipfile.ZipFile(cover_path) as z:
                    for name in z.namelist():
                        if "cover" in name.lower() and name.endswith((".jpeg", ".jpg", ".png")):
                            cover_bytes = z.read(name)
                            break
            elif cover_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                cover_bytes = cover_path.read_bytes()

    builder = EpubBuilder(title=title, author=author, cover_image_bytes=cover_bytes)
    for md_path in md_files:
        content = md_path.read_text(encoding="utf-8")
        first_line = content.splitlines()[0] if content.splitlines() else md_path.stem
        chap_title = first_line.lstrip("#").strip()
        builder.add_chapter_from_markdown(
            file_name=f"{md_path.stem}.xhtml",
            title=chap_title,
            md_content=content,
        )
        console.print(f"Added chapter: [green]{chap_title}[/green] from {md_path.name}")

    builder.write_epub(output_epub)
    console.print(f"[bold green]Successfully generated EPUB:[/bold green] {output_epub}")


@main.command(name="colab-status")
def colab_status():
    """Check Google Colab CLI status in WSL."""
    bridge = ColabBridge()
    console.print("[bold cyan]Checking WSL Google Colab CLI...[/bold cyan]")
    res = bridge.check_status()
    console.print(f"Return code: {res['returncode']}")
    if res["stdout"]:
        console.print("[green]Stdout:[/green]\n" + res["stdout"])
    if res["stderr"]:
        console.print("[yellow]Stderr:[/yellow]\n" + res["stderr"])


if __name__ == "__main__":
    main()
