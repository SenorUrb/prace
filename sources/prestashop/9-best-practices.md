# PrestaShop Best Practices

## Coding Standards

### PHP Coding Standards

```php
// PSR-12 / PSR-4 (PrestaShop 8.x se jimi řídí)

// Namespace pro třídy
namespace PrestaShop\Module\MyModule\Controller;

class ProductController
{
    // 4 spaces indentation
    public function getProduct()
    {
        // ...
    }
}

// Naming conventions
class ProductManager {}        // Třídy: PascalCase
public function getProduct()   // Metody: camelCase
private $productName;          // Properties: camelCase
const MAX_PRODUCTS = 100;      // Konstasy: UPPER_SNAKE_CASE
```

### File Structure

```
module/
├── src/
│   ├── Controller/
│   │   ├── Admin/
│   │   │   └── ProductController.php
│   │   └── Front/
│   │       └── ProductController.php
│   ├── Service/
│   │   └── ProductService.php
│   ├── Entity/
│   │   └── Product.php
│   └── Repository/
│       └── ProductRepository.php
├── views/
│   ├── templates/
│   ├── css/
│   └── js/
├── config/
│   ├── services.yml
│   └── routes.yml
├── tests/
├── translations/
└── module.php
```

## Security Best Practices

```php
// ✓ Vždy validuj input
$email = Tools::getValue('email');
if (!Validate::isEmail($email)) {
    $this->errors[] = 'Invalid email';
}

// ✓ Vždycky escapuj output
echo htmlspecialchars($user_input);

// ✓ Použ prepared statements
Db::getInstance()->execute(
    "SELECT * FROM product WHERE id = ?",
    [$id]
);

// ✓ Kontroluj permissions
if (!$this->context->employee->isSuperAdmin()) {
    die('Access denied');
}

// ✓ CSRF token v forms
<input type="hidden" name="token" value="{$token}">

// ✓ Hashuj hesla
password_hash($password, PASSWORD_BCRYPT)
```

## Code Quality

### SOLID Principles

**S - Single Responsibility**
```php
// ŠPATNĚ - Třída dělá moc
class Product {
    public function save() { }
    public function validate() { }
    public function sendEmail() { }  // To není v odpovědnosti Produktu
}

// SPRÁVNĚ - Oddělené třídy
class Product { public function save() { } }
class ProductValidator { public function validate() { } }
class ProductNotifier { public function sendEmail() { } }
```

**O - Open/Closed**
```php
// ŠPATNĚ - Přidáváme nové typy → měníme kód
class PaymentProcessor {
    public function process($type, $amount) {
        if ($type == 'stripe') { }
        else if ($type == 'paypal') { }
    }
}

// SPRÁVNĚ - Extensible, uzavřené pro změny
interface PaymentGateway {
    public function process($amount);
}

class StripeGateway implements PaymentGateway { }
class PaypalGateway implements PaymentGateway { }
```

**L - Liskov Substitution**
```php
// SPRÁVNĚ - Všechny implementace interface jsou zaměnitelné
$gateway = new StripeGateway();
processPayment($gateway);  // Funguje stejně s PaypalGateway
```

**I - Interface Segregation**
```php
// ŠPATNĚ - Fat interface
interface PaymentProcessor {
    public function pay();
    public function refund();
    public function recurring();
    public function validate3d();
}

// SPRÁVNĚ - Specifické interfaces
interface PaymentProcessor { public function pay(); }
interface Refundable { public function refund(); }
interface RecurringCapable { public function setupRecurring(); }
```

**D - Dependency Injection**
```php
// ŠPATNĚ - Hard dependency
class OrderService {
    private $emailSender = new EmailSender();
}

// SPRÁVNĚ - Injected dependency
class OrderService {
    private $emailSender;
    
    public function __construct(EmailSender $emailSender) {
        $this->emailSender = $emailSender;
    }
}
```

## Testing

### Unit Tests (PHPUnit)

```php
<?php
// tests/Unit/ProductTest.php
namespace PrestaShop\Tests\Unit;

use PHPUnit\Framework\TestCase;
use PrestaShop\Module\MyModule\Service\ProductService;

class ProductTest extends TestCase
{
    private $productService;
    
    protected function setUp(): void
    {
        $this->productService = new ProductService();
    }
    
    public function testGetProductPrice()
    {
        $price = $this->productService->getPrice(123);
        $this->assertEquals(999.99, $price);
    }
    
    public function testProductNotFound()
    {
        $this->expectException(ProductNotFoundException::class);
        $this->productService->getProduct(99999);
    }
}
```

### Integration Tests

```php
// tests/Integration/OrderTest.php
class OrderIntegrationTest extends TestCase
{
    public function testCompleteOrderFlow()
    {
        // 1. Vytvoř cart
        $cart = CartFactory::create();
        
        // 2. Přidej produkty
        $cart->addProduct(123, 2);
        
        // 3. Vytvoř order
        $order = OrderFactory::fromCart($cart);
        
        // 4. Ověř
        $this->assertEquals(2, $order->getTotalQuantity());
    }
}
```

### Running Tests

```bash
# Spusť všechny testy
./vendor/bin/phpunit

# Konkrétní test
./vendor/bin/phpunit tests/Unit/ProductTest.php

# Coverage report
./vendor/bin/phpunit --coverage-html=coverage/
```

## Performance Optimization

### Lazy Loading

```php
// ŠPATNĚ - Načti vše hned
$products = Product::getAll();

// SPRÁVNĚ - Lazy load
$products = new LazyCollection(function() {
    return Product::getPage(1);
});
```

### Caching Strategy

```php
public function getProduct($id)
{
    $cache_key = 'product_' . $id;
    
    // Zkus cache
    if ($cached = Cache::get($cache_key)) {
        return $cached;
    }
    
    // Fetch if not cached
    $product = new Product($id);
    
    // Cache for 1 hour
    Cache::set($cache_key, $product, 3600);
    
    return $product;
}
```

### Query Optimization

```php
// ŠPATNĚ - N+1 queries
foreach ($products as $product) {
    $images = $product->getImages();  // Query v loopu!
}

// SPRÁVNĚ - Single query s joinů
$sql = "SELECT p.*, i.id_image 
        FROM product p
        LEFT JOIN image i ON p.id_product = i.id_product";
```

## Documentation

### Code Comments

```php
// Komentuj ŘÍ?
// Jasné "co" a "proč", ne "jak"

// ŠPATNĚ
$x = $p * 1.21;  // Vynásoby cenou

// SPRÁVNĚ
$tax_amount = $price * 1.21;  // VAT is 21% in Czech Republic

// DOBRÉ - Complex algoritmus
/**
 * Calculate cumulative discount based on customer history
 * Discount tiers:
 * - 0-999 CZK: 0%
 * - 1000-4999 CZK: 5%
 * - 5000+ CZK: 10%
 */
private function calculateLoyaltyDiscount($totalSpent)
{
    // ...
}
```

### README.md

```markdown
# My Module

## Description
Co dělá modul a proč existuje

## Installation
1. Copy to /modules/
2. Enable in admin

## Configuration
Jak se konfiguruje

## Usage
Příklady jak se používá

## Testing
Jak se testuje

## Troubleshooting
Časté problému a řešení

## License
```

### API Documentation

```php
/**
 * Get product by ID
 * 
 * @param int $id_product Product ID
 * @param int $id_lang Language ID (default: 1)
 * 
 * @return Product
 * @throws ProductNotFoundException
 * 
 * @example
 * $product = getProduct(123);
 * echo $product->name;
 */
public function getProduct($id_product, $id_lang = 1)
{
    // ...
}
```

## Version Control

### Commit Messages

```bash
# Dobré commit messages
git commit -m "Fix: Prevent SQL injection in product search"
git commit -m "Feature: Add loyalty discount calculation"
git commit -m "Refactor: Extract ProductService from Controller"
git commit -m "Chore: Update dependencies"

# Špatné
git commit -m "Fix stuff"
git commit -m "WIP"
git commit -m "Asdf"
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/new-discount-system

# Work na feature
git add .
git commit -m "Feature: Implement discount calculation"

# Push a create PR
git push origin feature/new-discount-system

# Code review → merge to main
```

## Environment Management

```
.env (development)
.env.example (template, version controlled)
.env.production (production settings)
.gitignore (exclude .env)
```

```php
// .env
DATABASE_HOST=localhost
DATABASE_NAME=prestashop_dev
DEBUG=true

// Access in code
$host = getenv('DATABASE_HOST');
```

## Module Development Checklist

### Development Phase
- [ ] Vytvořená základní struktura
- [ ] Implementovány feature
- [ ] Code reviewed
- [ ] Unit testy napsány
- [ ] Integration testy napsány
- [ ] Security audit provedenm
- [ ] Performance testováno

### Pre-Release
- [ ] Dokumentace napsána
- [ ] Lokalizace (translations) hotova
- [ ] Kompatibilita testována (PS verze)
- [ ] Kompatibilita testována (PHP verze)
- [ ] SQL migrations hotovy
- [ ] Error handling hotov

### Release
- [ ] Version bump (SEMVER)
- [ ] Changelog updated
- [ ] Git tag created
- [ ] Package distribution ready
- [ ] Installation guide updated

### Post-Release
- [ ] Monitor error logs
- [ ] Support for issues
- [ ] Security patches pokud je potřeba
- [ ] Community feedback

## Otázky k Pohovoru

- Jaké jsou SOLID principy?
- Jak píšeš unit testy?
- Jaké je tvoje názorům na code review?
- Jak strukturuješ projekt?
- Jak se vyhybuješ N+1 queries?
- Jak dokumentuješ kód?
- Jaké jsou best practices pro git?
- Jak se vyvíjí modulem v týmu?
- Jak řešíš versionování API?
- Jaké jsou antipatterns kterých se vyhybuješ?
