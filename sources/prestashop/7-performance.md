# PrestaShop Performance Optimizace

## Caching Strategie

### Front-end Cache

```php
// Vypnut cache v debug módu
define('_PS_DEBUG_SQL_', false);
define('_PS_DEBUG_', false);

// Cache soubory
if (!$this->isCacheable()) {
    return; // Necachuj
}

// Cachuj data
$cache_key = md5(serialize($params));
if ($cached = Cache::retrieve($cache_key)) {
    return json_decode($cached);
}

// Ulož v cachoe
$data = expensiveQuery();
Cache::store($cache_key, json_encode($data), 3600);  // 1 hodina
```

### Database Query Caching

```php
// Nakeshuj produkty (PS 1.7)
$cache = new Cache();
$cache->write(
    'product_' . $id_product,
    serialize($product->getFields()),
    3600  // TTL v sekundách
);

// Retrieve
$cached = $cache->read('product_' . $id_product);
if ($cached) {
    return unserialize($cached);
}
```

### Cache Layers

```
1. Browser Cache         // Obrázky, CSS, JS (30 dní)
2. CDN Cache            // Statické assety (7 dní)
3. Page Cache           // HTML stránky (1 hodina)
4. Query Cache          // Běžné SQL (15 minut)
5. Object Cache (Redis) // PHP objekty (session, config)
```

## Database Optimization

### Indexing

```sql
-- Před optimalizací
SELECT * FROM ps_order WHERE id_customer = 5;  -- Slow!

-- Přidej index
ALTER TABLE `ps_order` ADD INDEX `idx_customer` (`id_customer`);
SELECT * FROM ps_order WHERE id_customer = 5;  -- Fast!
```

### Explain Query Plans

```sql
EXPLAIN SELECT * FROM ps_product WHERE active = 1;
-- Vidíš:
-- rows: 50000    (kolik řádků se prohledalo)
-- key: idx_active (jaký index se použil)
-- type: ref      (typ lookup - const, ref, range, index, ALL)
```

### Worst Case: Full Table Scan
```sql
-- BAD - všechny řádky se prohledávají
SELECT * FROM ps_product WHERE YEAR(date_add) = 2024;
-- Zlepšení:
SELECT * FROM ps_product 
WHERE date_add >= '2024-01-01' AND date_add < '2025-01-01';
```

## PHP Code Optimization

### Avoid Loops with Queries

```php
// ŠPATNĚ - N+1 queries
$products = Product::getRandomProducts();
foreach ($products as $product) {
    $images = Image::getImages($id_lang, $product['id_product']);  // Query v loopu!
}

// DOBŘE - Single query
$sql = "SELECT p.*, i.id_image 
        FROM product p
        LEFT JOIN image i ON p.id_product = i.id_product
        WHERE p.active = 1";
$data = Db::getInstance()->executeS($sql);
```

### Cache Expensive Operations

```php
// Drahá operace - výpočet ceny s daní
public function getPriceWithTax($id_product)
{
    $cache_key = 'price_tax_' . $id_product;
    
    // Zkus cache
    if ($cached = Cache::retrieve($cache_key)) {
        return $cached;
    }
    
    // Drahá operace
    $price = $this->calculatePriceWithTax($id_product);
    
    // Ulož v cachoe
    Cache::store($cache_key, $price, 3600);
    
    return $price;
}
```

### Lazy Loading

```php
// Neinicializuj všechno najednou
$products = Product::getAll();  // Mělo by být paginováno!

// Rozděl na stránky
$page = (int)Tools::getValue('p', 1);
$per_page = 20;
$start = ($page - 1) * $per_page;

$products = Db::getInstance()->executeS("
    SELECT * FROM product 
    WHERE active = 1 
    LIMIT $start, $per_page
");
```

## Image Optimization

### Compression
```php
// Kompresi obrázky při uploadu
public function compressImage($source, $destination)
{
    $image = imagecreatefromjpeg($source);
    imagejpeg($image, $destination, 85);  // 85% quality
    imagedestroy($image);
}
```

### Responsive Images
```html
<!-- Twig - responsive -->
<picture>
  <source media="(max-width: 600px)" 
          srcset="{{ product.image_small }}">
  <source media="(min-width: 601px)" 
          srcset="{{ product.image_large }}">
  <img src="{{ product.image }}" alt="{{ product.name }}">
</picture>
```

### Lazy Loading
```html
<!-- Twig -->
<img loading="lazy" 
     src="{{ product.image }}" 
     alt="{{ product.name }}">
```

## CSS & JS Minimization

```php
// V theme assets
$this->context->controller->addCSS(_THEME_CSS_DIR_ . 'main.css');
$this->context->controller->addJS(_THEME_JS_DIR_ . 'main.js');

// V produkci se automaticky minifikuje
// PrestaShop hledá .min.css a .min.js
```

### Manual Build

```bash
# NPM build
npm install
npm run build  # Vytvoří min.js a min.css
```

## Server-side Performance

### PHP Settings
```php
// php.ini optimalizace
max_execution_time = 30
memory_limit = 128M
upload_max_filesize = 10M
post_max_size = 10M

// OPcache (caching PHP bytecode)
opcache.enable = 1
opcache.memory_consumption = 128
```

### Cron Jobs
```php
// PS Task Scheduler
// Běží maintenance tasky na pozadí
- Objednavky cleanup
- Databáze optimalizace
- Cache clearing
- Stats aktualizace

// Configuj v admin: System > Maintenance > Scheduled tasks
```

## Front-end Performance

### Critical Rendering Path
```html
<!-- Inline critical CSS -->
<style>
  /* Critical path styles - layout, above-the-fold */
  header { /* ... */ }
  .hero { /* ... */ }
</style>

<!-- Defer non-critical -->
<link rel="preload" as="style" href="main.css" 
      onload="this.onload=null;this.rel='stylesheet'">

<!-- Async scripts -->
<script async src="analytics.js"></script>

<!-- Defer scripts - spusti se až po DOM load -->
<script defer src="app.js"></script>
```

### Performance Metrics

Měř pomocí:
- Google PageSpeed Insights
- GTmetrix
- WebPageTest
- Chrome DevTools

Klíčové metriky:
- **FCP** (First Contentful Paint) < 1.8s
- **LCP** (Largest Contentful Paint) < 2.5s
- **CLS** (Cumulative Layout Shift) < 0.1
- **TTFB** (Time to First Byte) < 600ms

## Monitoring & Profiling

### Query Profiling

```php
// Zapni SQL logging (debug mode)
define('_PS_DEBUG_SQL_', true);

// Podívej se na queries v /var/logs/sql-errors.log
```

### PHP Profiling

```php
// Měř čas funkce
$start = microtime(true);
expensiveFunction();
$end = microtime(true);
error_log('Time: ' . ($end - $start) . 's');
```

## Benchmarks

Typické metriky pro zdravý shop:

| Metrika | Cíl | Varovný sign |
|---------|-----|-------------|
| Page Load | < 2s | > 3s |
| DB Query Count | < 50 | > 100 |
| Memory Usage | < 32MB | > 64MB |
| Image Size (homepage) | < 1MB | > 3MB |
| Time to Interactive | < 3s | > 5s |

## Otázky k Pohovoru

- Jak optimalizuješ database queries?
- Co je N+1 problem a jak se řeší?
- Jak funguje caching v PS?
- Jaké indexy bysi přidal?
- Jak měříš performance?
- Jak optimalizuješ obrázky?
- Jaký je Critical Rendering Path?
- Jak se minifikuje CSS a JS?
- Jak se měří Front-end metriky?
- Jak se debuguje pomalý shop?
