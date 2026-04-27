#!/usr/bin/env python3
"""
pdf_to_md.py
Převod PDF souborů na Markdown.
Použití:
  python3 pdf_to_md.py --input <input_dir> --output <output_dir>

Skript se pokusí použít `pypdf` pro extrakci textu.
Pokud není dostupný, zkusí `pdftotext` z poppleru.
"""
import os
import sys
import argparse
import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    # nahraď nepovolené znaky pomlčkou
    name = re.sub(r"[^A-Za-z0-9._-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name


def extract_with_pypdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        raise
    text_parts = []
    reader = PdfReader(str(path))
    for p in reader.pages:
        try:
            t = p.extract_text()
        except Exception:
            t = None
        if t:
            text_parts.append(t)
    return "\n\n".join(text_parts)


def extract_with_pdftotext(path: Path) -> str:
    import subprocess
    cmd = ["pdftotext", str(path), "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {err.decode('utf-8', errors='ignore')}" )
    return out.decode("utf-8", errors="ignore")


def normalize_text(text: str) -> str:
    # Odstraň přebytečné prázdné řádky
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim
    return text.strip() + "\n"


def convert_pdf(path: Path, outdir: Path):
    basename = path.stem
    outname = sanitize_filename(basename) + ".md"
    outpath = outdir / outname

    # extrakce
    text = None
    try:
        text = extract_with_pypdf(path)
    except Exception:
        try:
            text = extract_with_pdftotext(path)
        except Exception as e:
            print(f"Chyba při čtení {path}: {e}", file=sys.stderr)
            return None

    if not text:
        print(f"Žádný text z {path}", file=sys.stderr)
        return None

    text = normalize_text(text)

    # Přidej jednoduchý nadpis a metadata
    header = f"# {path.name}\n\n"
    meta = f"- source: {path.name}\n- size: {path.stat().st_size} bytes\n\n"

    content = header + meta + text

    with open(outpath, "w", encoding="utf-8") as f:
        f.write(content)

    return outpath


def main():
    parser = argparse.ArgumentParser(description="Convert PDFs to Markdown files.")
    parser.add_argument("--input", "-i", required=True, help="Input directory with PDFs")
    parser.add_argument("--output", "-o", required=True, help="Output directory for MD files")
    parser.add_argument("--ext", default=".pdf", help="File extension to search for")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(2)

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() == args.ext.lower()])
    if not files:
        print("No PDF files found.")
        sys.exit(0)

    print(f"Found {len(files)} files. Converting...")
    results = []
    for p in files:
        print(f"- {p.name}")
        out = convert_pdf(p, output_dir)
        if out:
            results.append(out)

    print(f"Converted {len(results)} / {len(files)} files.")

if __name__ == '__main__':
    main()
