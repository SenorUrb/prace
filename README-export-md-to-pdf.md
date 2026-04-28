Export Markdown → PDF (Pandoc + XeLaTeX)

Rychlý návod, jak převést Markdown (.md) na PDF včetně lokálních obrázků.

Požadavky
- macOS: nainstalovaný `pandoc` a LaTeX (XeLaTeX). Doporučeno: MacTeX nebo BasicTeX.
- Alternativy: `wkhtmltopdf`, nebo Docker image s pandoc, pokud nechcete instalovat LaTeX lokálně.

Instalace (macOS)
- Pandoc: `brew install pandoc`
- MacTeX (plná instalace): stáhnout z https://tug.org/mactex/ nebo `brew install --cask mactex`
- Pokud chcete menší variantu: BasicTeX + potřebné balíčky.

Základní příkaz

pandoc /cesta/k/soubor.md -o /cesta/k/soubor.pdf --from markdown --pdf-engine=xelatex --resource-path=/cesta/k/projekt:/cesta/k/projekt/assets/img/

Vysvětlení
- `--pdf-engine=xelatex` — používá XeLaTeX (lepší podpora fontů než pdfTeX).
- `--resource-path` — složky, kde pandoc hledá obrázky (oddělené dvojtečkou na macOS/Linux).
- V Markdownu používejte relativní cesty k obrázkům, např. `![Alt](assets/img/martin_urbanek.jpeg)`.

Doporučený příklad (projekt v /Users/you/Downloads/prace):

pandoc /Users/you/Downloads/prace/CV-Martin-Urbanek-2026.md -o /Users/you/Downloads/prace/CV-Martin-Urbanek-2026.pdf --from markdown --pdf-engine=xelatex --resource-path=/Users/you/Downloads/prace:/Users/you/Downloads/prace/assets/img/

Tipy
- Pokud se objeví chyba „file does not exist", použijte absolutní cesty nebo spusťte příkaz z kořenové složky projektu.
- Emoji (např. 📫) nemusí být v PDF vykreslené — XeLaTeX nemusí mít barevné emoji fonty. Odstraňte emoji nebo nahraďte textem, pokud se objeví varování.
- Pro problémy s chybějícími znaky nastavte hlavní font: `--variable mainfont="DejaVu Sans"` (DejaVu fonty je třeba mít nainstalované).

Příklad s nastaveným fontem:

pandoc CV.md -o CV.pdf --from markdown --pdf-engine=xelatex --variable mainfont="DejaVu Sans" --resource-path=.:assets/img/

Docker alternativa

Pokud nechcete instalovat pandoc/LaTeX lokálně, použijte Docker (může být potřeba přizpůsobit image):

Docker (příklad):

docker run --rm -v "$(pwd)":/data pandoc/core:latest pandoc CV.md -o CV.pdf --from markdown --pdf-engine=xelatex --resource-path=.:assets/img/

Časté potíže & řešení
- `Missing character` upozornění: znamená, že aktuální LaTeX font nepodporuje znak (často emoji). Řešení: odstranit emoji nebo použít font podporující znak.
- `withBinaryFile: does not exist`: špatná cesta k .md souboru — ověřte, že soubor existuje a dejte absolutní cestu.
- Obrázky se nezobrazí: zkontrolujte `--resource-path` a relativní cesty v Markdownu.

Chcete, abych teď spustil export vašeho CV do PDF (opět) s aktuálním nastavením? Pokud ano, potvrďte a já to spustím.