# PrestaShop Architektura

## MVC Model

PrestaShop následuje **MVC (Model-View-Controller)** architekturu:

### Models (Modely)
- Umístění: `/classes/`
- Dědí z `ObjectModel`
- Reprezentují tabulky v databázi
- Obsahují business logic

Příklad:
```php
class Product extends ObjectModel
{
    public $id_product;
    public $name;
    public $description;
    public $price;
    
    public static $definition = [
        'table' => 'product',
        'primary' => 'id_product',
        'fields' => [
            'name' => ['type' => 'string', 'required' => true],
            'price' => ['type' => 'float'],
        ]
    ];
}
```

### Controllers (Řadiče)
- Umístění: `/controllers/`
- Front-end: `/controllers/front/`
- Admin: `/controllers/admin/`
- Handling HTTP requestů, logika
- Předávají data do templates

Příklad front-end controller:
```php
class ProductController extends FrontController
{
    public function init()
    {
        parent::init();
    }
    
    public function initContent()
    {
        $product = new Product((int)Tools::getValue('id_product'));
        $this->context->smarty->assign('product', $product);
        parent::initContent();
    }
}
```

### Views (Pohledy)
- Umístění: `/views/` nebo `/templates/`
- Twig templating (PS 8.x) nebo Smarty (PS 1.7)
- Zobrazení dat pro uživatele
- Frontend HTML + CSS

## Directory Structure

```
prestashop/
├── admin/              # Admin panel
├── classes/            # Models a business logic
├── controllers/        # Controllers
│   ├── admin/
│   ├── front/
│   └── modular/
├── modules/            # Moduly (rozšíření)
├── themes/             # Themes (templates)
├── views/              # Views pro admin
├── config/             # Konfigurace
├── cache/              # Cache soubory
├── download/           # Downloadable produkty
├── translations/       # Jazykové soubory
└── upload/             # User uploaded files
```

## Request Lifecycle

```
1. index.php zavolán
2. Dispatcher určí controller
   - URL rozhoduje který controller
   - napr. /product/123 → ProductController
3. Init phase
   - Context inicializace
   - Database připojení
   - Settings načtení
4. Execute phase
   - Init metoda
   - postProcess (POST data)
   - initContent (GET data + display)
5. Render phase
   - smarty->display()
   - HTML vrácen
```

### Příklad URL struktura:
```
/product/123-my-product-name
  → class_name = "Product"
  → id_product = 123
  
/admin/?controller=AdminProducts&token=xxx
  → class_name = "AdminProducts"
  → Admin panel action
```

## Context Object

Centrální objekt dostupný všude:

```php
$this->context->shop        // Aktuální shop info
$this->context->customer    // Přihlášený zákazník
$this->context->cart        // Nákupní košík
$this->context->currency    // Měna
$this->context->language    // Jazyk
$this->context->employee    // Přihlášený admin
$this->context->link        // Link generátor
$this->context->smarty      // Template engine
$this->context->db          // Database
```

## FrontController vs AdminController

### FrontController
- Veřejný web, zákazníci
- Sekuritu - HTTPS, cookies
- Session management
- Cart, orders
- SSL check

### AdminController
- Admin panel
- Employee přístup
- Permission checks
- Token validace (CSRF ochranu)
- Audit logging

## Multistore Support

PrestaShop podporuje více obchodů v jedné instanci:

```php
$shops = Shop::getShops();  // Všechny shops

// Shop kontext
$shop_id = $this->context->shop->id;
$all_shops = Shop::getShops(true); // Disabled shops také
```

- Sdílená databáze
- Odlišné domény/SSL certy
- Oddělené katalogy/ordery
- Sdílené zákazníky (optional)

## Lifecycle Hooks

### Init phase
- `actionFrontControllerInit` - Frontend controller init
- `actionAdminControllerInit` - Admin controller init

### Processing phase
- `actionPostProcess` - Po zpracování POST

### Display phase
- `actionFrontControllerSetMedia` - Assets loading
- `actionBeforeRender` - Před vyrenderováním
- `actionAfterRender` - Po vyrenderování

## Bezpečnostní Důležité Body

1. **HTTPS/SSL** - Vždy použít na live
2. **SQL Injection** - Nikdy nepoužívat \`\$_GET\` přímo
3. **XSS** - Validovat a sanitizovat všechny výstupy
4. **CSRF Token** - Všechny admin formuláře musí mít token
5. **Permissiony** - Kontrolovat access na všech nízkých úrovních

## Otázky k Pohovoru

- Jak funguje MVC v PrestaShopu?
- Co je Context objekt a jak se používá?
- Jaký je rozdíl mezi FrontController a AdminController?
- Jak funguje URL routing?
- Jaké jsou kroky Request Lifecycle?
- Jak se Multistore režim liší od single-shop?
- Kde se modul kód umisťuje?
