---
name: nabidky-pdf-export
description: "Use when exporting z Markdownu do PDF. Pouziva znovupouzitelny skript scripts/export_md_to_pdf/export_md_to_pdf.sh."
---

# Export nabidek do PDF

Pouzij tento skill, kdyz je potreba prevest hotovou nabidku z Markdownu do PDF.

## Kdy pouzit
- Kdyz uzivatel pozada o PDF verzi.

## Standardni postup
1. Over, ze existuje vstupni markdown soubor ve vystupy.
2. Spust export pomoci skriptu:
   - scripts/export_md_to_pdf/export_md_to_pdf.sh vystupy/<soubor>.md
3. Over, ze vznikl vystupni PDF soubor vedle markdownu.

## Volitelny vystupni nazev
- scripts/export_md_to_pdf/export_md_to_pdf.sh vystupy/<soubor>.md vystupy/<soubor>.pdf

## Poznamky
- Tento workflow preferuj pred ad-hoc prikazy, aby byl export konzistentni.
- Pokud skript neexistuje, vytvor jej v scripts/export_md_to_pdf/export_md_to_pdf.sh a nastav spustitelny bit.
