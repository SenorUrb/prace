#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Pouziti: $0 <vstup.md> [vystup.pdf]"
  exit 1
fi

INPUT_MD="$1"
if [[ ! -f "$INPUT_MD" ]]; then
  echo "Chyba: vstupni soubor neexistuje: $INPUT_MD"
  exit 1
fi

if [[ $# -eq 2 ]]; then
  OUTPUT_PDF="$2"
else
  OUTPUT_PDF="${INPUT_MD%.md}.pdf"
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Chyba: pandoc neni nainstalovany nebo neni v PATH."
  exit 1
fi

pandoc "$INPUT_MD" --pdf-engine=xelatex -o "$OUTPUT_PDF"
echo "PDF vytvoreno: $OUTPUT_PDF"