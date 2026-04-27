pdf_to_md.py — převod PDF do Markdown

Usage:

```bash
python3 scripts/pdf_to_md.py --input job-offers/1webIT --output job-offers/1webIT
```

Co skript dělá:
- Projde zadanou složku a najde všechny `.pdf` soubory
- Extrahuje text (přes `pypdf` nebo `pdftotext`) a normalizuje ho
- Uloží výsledek jako `.md` se stejným názvem (sanitizovaným)

Poznámky:
- Doporučeno mít nainstalované `pypdf` (`pip install pypdf`) nebo `pdftotext` z poppleru.
- Skript může vynechat komplexní layout PDF (tabulky, obrázky).