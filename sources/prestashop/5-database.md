# PrestaShop Databáze a ORM

## Databázová Struktura

PrestaShop používá relační databázi (MySQL/MariaDB) se specifickou strukturou:

```
Database Tables (> 100 tabulek)

Klíčové tabulky:
- ps_product              # Produkty
- ps_product_lang        # Jazyková verze produktů
- ps_category            # Kategorie
- ps_customer            # Zákazníci
- ps_orders              # Objednávky
- ps_order_detail        # Detaily objednávek
- ps_address             # Adresy
- ps_attribute           # Atributy produktů
- ps_attribute_lang      # Jazykové verze atributů
- ps_image               # Obrázky produktů
- ps_stock               # Skladové zásoby
- ps_cart                # Nákupní košíky
- ps_cart_product        # Produkty v košíku
```

## ObjectModel - ORM

PrestaShop má vlastní lightweight ORM - `ObjectModel`:

```php
class Product extends ObjectModel
{
    // Definice tabulky a sloupců
    public static $definition = [
        'table' => 'product',
        'primary' => 'id_product',
        'multilang' => true,  // Tabulka má jazykové verze
        'fields' => [
            'reference' => ['type' => 'string', 'size' => 32],
            'price' => ['type' => 'price'],
            'active' => ['type' => 'bool', 'validate' => 'isBool'],
            'name' => [
                'type' => 'string',
                'lang' => true,  // Jazyková verze
                'validate' => 'isGenericName',
                'required' => true,
            ],
        ]
    ];
    
    // Veřejné properties
    public $id_product;
    public $reference;
    public $price;
    public $active = 1;
}
```

## Práce s Objekty

### Vytvoření
```php
$product = new Product();
$product->name = 'Nový Produkt';
$product->price = 999.99;
$product->active = 1;
$product->save();
```

### Načtení
```php
// ID podle primárního klíče
$product = new Product(123);
echo $product->name;

// Vícejazační model
$product = new Product(123, $id_lang = 1);  // ID jazyka
```

### Aktualizace
```php
$product = new Product(123);
$product->price = 1299.99;
$product->save();
```

### Smazání
```php
$product = new Product(123);
$product->delete();
```

## Databázové Dotazy

### Přímé SQL (pokud ObjectModel nestačí)

```php
// SELECT
$results = Db::getInstance()->executeS("
    SELECT * FROM product WHERE active = 1
");

// Single row
$product = Db::getInstance()->getRow("
    SELECT * FROM product WHERE id_product = ?
", [123]);

// Single value
$count = Db::getInstance()->getValue("
    SELECT COUNT(*) FROM product WHERE active = 1
");

// Execute (INSERT, UPDATE, DELETE)
Db::getInstance()->execute("
    UPDATE product SET price = ? WHERE id_product = ?
", [999.99, 123]);
```

### Prepared Statements (bezpečné)

```php
// Vždycky používej placeholdery ?
$results = Db::getInstance()->executeS("
    SELECT * FROM product 
    WHERE name LIKE ? AND price > ? AND active = ?
", ['%phone%', 100, 1]);

// Vrátí pole polí
foreach ($results as $row) {
    echo $row['name'];
}
```

## Multilingual Support

PrestaShop má vestavěné jazykové verze:

```php
// Načti v konkrétním jazyce
$product = new Product(123, $id_lang = 2);  // ID jazyka 2
echo $product->name;  // Jméno v jazyce 2

// Všechny jazyky
$languages = Language::getLanguages();
foreach ($languages as $lang) {
    $product = new Product(123, $lang['id_lang']);
    echo "Name in {$lang['name']}: {$product->name}";
}
```

SQL struktura:
```
ps_product              # Základní data (bez jazykových věcí)
ps_product_lang        # name, description (s id_lang)
ps_category
ps_category_lang       # name, description
```

## Relace Mezi Tabulkami

### One-to-Many
```php
// Jeden produkt má mnoho obrázků
$images = Image::getImages($id_lang, $id_product);
foreach ($images as $image) {
    echo $image['id_image'];
}
```

### Many-to-Many
```php
// Produkt má mnoho atributů, atribut má mnoho produktů
$attributes = $product->getAttributes();
foreach ($attributes as $attr) {
    echo $attr['name'];
}
```

## Transactions

```php
Db::getInstance()->beginTransaction();

try {
    // Aktualizuj cenu
    Db::getInstance()->execute(
        "UPDATE product SET price = ? WHERE id_product = ?",
        [999.99, 123]
    );
    
    // Ulož v historii
    Db::getInstance()->insert('price_history', [
        'id_product' => 123,
        'price' => 999.99,
        'date' => date('Y-m-d H:i:s'),
    ]);
    
    Db::getInstance()->commit();
} catch (Exception $e) {
    Db::getInstance()->rollBack();
    throw $e;
}
```

## Migration & Installation

```php
// Vytvoření tabulky v modulu
private function installDatabase()
{
    $sql = "CREATE TABLE IF NOT EXISTS `" . _DB_PREFIX_ . "mydata` (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `id_product` INT NOT NULL,
        `data` TEXT,
        `date_add` DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (`id_product`) REFERENCES `" . _DB_PREFIX_ . "product`(`id_product`)
    ) ENGINE=InnoDB;";
    
    return Db::getInstance()->execute($sql);
}

// Smazání
private function uninstallDatabase()
{
    return Db::getInstance()->execute(
        "DROP TABLE IF EXISTS `" . _DB_PREFIX_ . "mydata`"
    );
}
```

## Query Builder (PS 8.x - modernější)

```php
// PS 8.x - Doctrine QueryBuilder
$products = $this->connection->createQueryBuilder()
    ->select('p.id_product, p.name, p.price')
    ->from(_DB_PREFIX_ . 'product', 'p')
    ->where('p.active = :active')
    ->setParameter('active', 1)
    ->orderBy('p.name', 'ASC')
    ->execute()
    ->fetchAllAssociative();
```

## Performance - N+1 Problem

### NEBEZPEČNĚ - N+1 queries
```php
$products = Product::getAll();
foreach ($products as $product) {
    // Každá iterace = 1 query
    $images = Image::getImages($id_lang, $product['id_product']);
    echo count($images);
}
// 1 query + N queries = N+1 problem!
```

### BEZPEČNĚ - Single query
```php
$sql = "SELECT p.id_product, p.name, COUNT(i.id_image) as image_count
        FROM product p
        LEFT JOIN image i ON p.id_product = i.id_product
        GROUP BY p.id_product";
$products = Db::getInstance()->executeS($sql);
// Jen 1 query!
```

## Indexing

```sql
-- Přidej index na často používané sloupce
ALTER TABLE `ps_product` ADD INDEX `idx_active` (`active`);
ALTER TABLE `ps_product` ADD INDEX `idx_name` (`id_product`, `active`);

-- Composite index pro WHERE clauses
ALTER TABLE `ps_order` ADD INDEX `idx_customer_date` 
  (`id_customer`, `date_add`);
```

## Otázky k Pohovoru

- Co je ObjectModel a jak se používá?
- Jak vytvoříš nový produkt?
- Jak se pracuje s vícejazykými daty?
- Jaké jsou klíčové tabulky v PS?
- Jak se provádějí bezpečné SQL dotazy?
- Co je N+1 problem a jak se řeší?
- Jak se používají transactions?
- Jaký je rozdíl mezi objektovým a SQL přístupem?
- Jak by sis přidal indexy?
- Jak se migrují data?
