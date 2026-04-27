# PrestaShop - Časté Problémy a Řešení

## Problém 1: Module se neinstalovuje

**Symptom:**
```
Error: Unable to install module
```

**Běžné příčiny:**

1. **Missing `__construct`**
   ```php
   // ŠPATNĚ
   class MyModule extends Module { }
   
   // SPRÁVNĚ
   class MyModule extends Module {
       public function __construct() {
           $this->name = 'mymodule';
           parent::__construct();
       }
   }
   ```

2. **Chybějící `install()` metoda**
   ```php
   public function install() {
       if (!parent::install()) {
           return false;
       }
       // Registruj hooky, vytvoř tabulky, atd.
       return true;
   }
   ```

3. **SQL chyba při instalaci**
   ```php
   public function install() {
       // Loguj SQL error
       if (!Db::getInstance()->execute($sql)) {
           $error = Db::getInstance()->getMsgError();
           error_log("SQL Error: " . $error);
           return false;
       }
       return parent::install();
   }
   ```

**Řešení:**
- Kontroluj `/var/logs/system.log`
- Ověř SQL syntax
- Zkontroluj práva adresáře `/modules/`

---

## Problém 2: Product se neaktualizuje

**Symptom:**
```
Změním cenu v admin, ale na front-endu se nezmění
```

**Příčina:**
Forgot to invalidate cache!

**Řešení:**
```php
// Po změně produktu invaliduj cache
$product = new Product($id_product);
$product->price = 1999.99;
$product->save();

// Smaž cache!
Cache::clean('product_*');
// nebo
Cache::clean('product_' . $id_product);
// nebo celý cache
Cache::clean();
```

---

## Problém 3: Module nezobrazuje output

**Symptom:**
```
Zaregistruji hook, implementuji metodu, nic se nezobrazuje
```

**Debugování:**
```php
public function hookDisplayProductContainer($params)
{
    // 1. Zkontroluj že se hook zavolá
    error_log('Hook called');
    
    // 2. Zkontroluj že se vrátí string
    $output = '<div>Test</div>';
    error_log('Output: ' . $output);
    
    return $output;
}

// Vidíš chyby v /var/logs/system.log
```

**Běžné příčiny:**
- Hook není zaregistrován (zavolej `install()`)
- Špatné jméno hooké metody
- Vrací null místo stringu
- CSS/JS soubory nejsou zahrnuty

---

## Problém 4: SQL Injection chyba (bezpečnost)

**Symptom:**
```
Útočník vstoupí ?id=1 OR 1=1 a získá všechny data
```

**ŠPATNĚ:**
```php
$id = $_GET['id'];
$product = Db::getInstance()->getRow(
    "SELECT * FROM product WHERE id_product = $id"
);
```

**SPRÁVNĚ:**
```php
$id = (int)Tools::getValue('id_product');
$product = Db::getInstance()->getRow(
    "SELECT * FROM product WHERE id_product = ?",
    [$id]
);
```

---

## Problém 5: Velký počet produktů - pomalé loading

**Symptom:**
```
Shop má 100,000 produktů a všechno je pomalé
```

**Řešení 1: Pagination**
```php
$page = (int)Tools::getValue('p', 1);
$per_page = 20;
$start = ($page - 1) * $per_page;

$products = Product::getProducts(
    $id_lang,
    $start,
    $per_page,
    'name',
    'asc'
);
```

**Řešení 2: Database Indexing**
```sql
-- Přidej indexy na často filtrované sloupce
ALTER TABLE `ps_product` ADD INDEX `idx_active` (`active`);
ALTER TABLE `ps_product` ADD INDEX `idx_category` (`id_category_default`);
ALTER TABLE `ps_product` ADD INDEX `idx_name_lang` 
  (`id_product`, `id_lang`);
```

**Řešení 3: Caching**
```php
$cache_key = 'products_page_' . $page;
if ($cached = Cache::retrieve($cache_key)) {
    return json_decode($cached);
}

// Fetchuj a cachuj na 1 hodinu
$products = expensiveQuery();
Cache::store($cache_key, json_encode($products), 3600);
```

---

## Problém 6: Image se nezobrazuje

**Symptom:**
```
Uploadnu obrázek, ale se nevidí
```

**Příčiny:**
1. **Image soubor není na disku**
   ```php
   // Zkontroluj
   $image_path = _PS_IMG_DIR_ . 'p/' . $id_product . '.jpg';
   if (!file_exists($image_path)) {
       error_log('Image not found: ' . $image_path);
   }
   ```

2. **Permission problem**
   ```bash
   chmod -R 755 /prestashop/img/
   chown -R www-data:www-data /prestashop/img/
   ```

3. **Image není v databázi**
   ```php
   // Zkontroluj v DB
   SELECT * FROM ps_image WHERE id_product = 123;
   // Pokud je prázdné, insert do DB
   ```

---

## Problém 7: CSRF Token error

**Symptom:**
```
Error: Invalid CSRF token
```

**Příčina:**
Token je zastaralý nebo chybí v formuláři

**Řešení:**
```php
// V šabloně (Twig)
<form method="POST">
    <input type="hidden" name="token" value="{{ token }}">
    <!-- ... -->
</form>

// V controlleru ověř token
$token = Tools::getValue('token');
if (empty($token) || !Tools::validateToken($token)) {
    die('Invalid token');
}
```

---

## Problém 8: Multi-language problémy

**Symptom:**
```
Změním produkt v češtině, ale angličtina se neuloží
```

**Řešení:**
```php
// Ulož pro VŠECHNY jazyky
$languages = Language::getLanguages();
$product = new Product(123);

foreach ($languages as $lang) {
    $product->name[$lang['id_lang']] = 'Product Name in ' . $lang['name'];
}

$product->save();
```

---

## Problém 9: Memory Limit Exceeded

**Symptom:**
```
Fatal error: Allowed memory size exhausted
```

**Příčina:**
Query vrátí moc dat najednou

**Řešení:**
```php
// ŠPATNĚ - vrátí všechno najednou
$all_products = Product::getAll();

// SPRÁVNĚ - stránkování
$page = 1;
$per_page = 100;
while (true) {
    $products = Db::getInstance()->executeS(
        "SELECT * FROM product LIMIT ?, ?",
        [($page-1)*$per_page, $per_page]
    );
    if (empty($products)) break;
    
    foreach ($products as $product) {
        // Process
    }
    
    $page++;
}
```

---

## Problém 10: Modul conflict

**Symptom:**
```
Dva moduly si kolidují v hooků
```

**Řešení:**
```php
// Zkontroluj ordery hooku
SELECT * FROM ps_hook_module 
WHERE id_hook = 5 
ORDER BY position;

// Změň position v admin: Module > Module list > Edit > Priority
```

---

## Debug Tools & Tips

### Error Logging
```php
// Loguj do souboru
error_log('Debug info: ' . print_r($data, true));

// Vidíš v /var/logs/system.log
```

### Database Query Logging
```php
// V config souboru zapni SQL logging
define('_PS_DEBUG_SQL_', true);

// Všechny queries budou v /var/logs/sql-errors.log
```

### Xdebug Setup
```php
// php.ini
zend_extension = xdebug.so
xdebug.mode = develop,debug
xdebug.start_with_request = trigger
```

### Profiling Execution Time
```php
$start = microtime(true);

// ... kód ...

$end = microtime(true);
error_log('Execution time: ' . ($end - $start) . ' seconds');
```

---

## Otázky k Pohovoru

- Co dělá když se modul neinstalovuje?
- Jak debuggeš modul který nic nerenduje?
- Co děláš když je shop pomalý?
- Jak řešíš memory limit problem?
- Co je SQL injection a jak se chrániš?
- Jak se zpracovává multi-language?
- Jak cachují data v PS?
- Jak se debugují hooky?
- Co dělá když je konflik mezi moduly?
- Jaké jsou best practices pro debugging?
