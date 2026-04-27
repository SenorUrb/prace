# PrestaShop - Průvodce pro pohovory

Komprehenzivní guide o PrestaShopu pro přípravu na technické pohovory. Obsahuje všechno, co by tě mohli ptát.

## Obsah

1. **[Architektura](architektura.md)** - MVC model, struktura aplikace, lifecycle
2. **[Modulární systém](moduly.md)** - Vývoj modulů, hooks, best practices
3. **[Themes a Templates](themes.md)** - Twig, Asset management, responsive design
4. **[Hooks a Events](hooks-events.md)** - Dispatcher, event system, custom hooks
5. **[Database](database.md)** - Struktura DB, ORM, ObjectModel
6. **[Bezpečnost](bezpecnost.md)** - CSRF, XSS, validace, sanitace
7. **[Performance](performance.md)** - Caching, optimalizace, measurement
8. **[Časté problémy](ceste-problemy.md)** - Debugging, common issues
9. **[Best Practices](best-practices.md)** - Coding standards, projekt struktura

## Základní informace

**Co je PrestaShop?**
- Open-source e-commerce platforma psaná v PHP
- Založena 2007, dnes je to jedna z nejpopulárnějších e-shopů
- Modulární architektura - rozšiřitelná prostřednictvím modulů
- Vícejazykový a multivalutový systém vestavěný

**Verze a kompatibilita:**
- PrestaShop 1.6, 1.7, 8.x (aktuální stabilní)
- PHP 7.2+ (1.7), PHP 8.0+ (8.x)
- MySQL/MariaDB 5.6+

**Klíčové komponenty:**
- Admin panel - full management e-shopu
- Front-end - customer facing store
- Modulární architektura
- Theme systém
- Payment gateways integrace
- Multi-vendor support

## Typické otázky v pohovoru

- Jak funguje modulární systém v PrestaShopu?
- Jaký je rozdíl mezi hooky a event dispatcherem?
- Jak optimalizuješ PrestaShop shop?
- Jaké bezpečnostní opatření je třeba udělat?
- Jak vyvíjíš a debuggeš vlastní modul?
- Jaké jsou limity PrestaShopu na velkých shopech?
- Jak zpracováváš platby a objednávky?
- Jak migraceješ z jednoho PrestaShopu na druhý?

## Quick Reference

### PrestaShop Version 8.x (nejnovější)
- Modernější PHP, Symfony komponenty
- Lepší performance
- Aktualizace bezpečnosti

### PrestaShop 1.7.x (stále rozšířený)
- Starší kód, ale stále funkční
- Více legacy modulů
- Menší community v posledních verzích

### Kdy se to napsalo?
- 2007 - PrestaShop 1.0
- 2013 - PS 1.6 (velkého popularity)
- 2016 - PS 1.7 (modernizace)
- 2021 - PS 8.0 (Symfony integraci)
