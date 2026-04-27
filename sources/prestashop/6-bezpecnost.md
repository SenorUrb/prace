# PrestaShop Bezpečnost

## Klíčové Bezpečnostní Hrozby

### 1. SQL Injection

**NEBEZPEČNĚ:**
```php
$id = $_GET['id'];
Db::getInstance()->query("SELECT * FROM product WHERE id_product = $id");
// Útočník: ?id=1 OR 1=1  // Vrátí všechny produkty!
```

**BEZPEČNĚ:**
```php
$id = (int)Tools::getValue('id_product');
Db::getInstance()->query("SELECT * FROM product WHERE id_product = $id");

// Nebo s prepared statements:
Db::getInstance()->execute("
    SELECT * FROM product WHERE id_product = ?
", [$id]);
```

### 2. Cross-Site Scripting (XSS)

**NEBEZPEČNĚ:**
```php
echo $_GET['search'];  // Útočník: <script>alert('hacked')</script>
echo $product->name;   // Pokud není escapován
```

**BEZPEČNĚ:**
```php
// Twig automaticky escapuje:
{{ product.name }}

// PHP - escape HTML:
echo htmlspecialchars($text, ENT_QUOTES, 'UTF-8');

// Smarty (PS 1.7):
{$product->name|escape:'html':'UTF-8'}
```

### 3. Cross-Site Request Forgery (CSRF)

**NEBEZPEČNĚ:**
```html
<form method="POST" action="/admin/">
  <input name="id_product" value="123">
  <button>Delete</button>
</form>
<!-- Bez CSRF tokenu - admin session se dá zneužít! -->
```

**BEZPEČNĚ v admin:**
```html
<form method="POST" action="/admin/">
  <input name="token" value="{$token}">
  <input name="id_product" value="123">
  <button>Delete</button>
</form>
```

```php
// V controleru ověř token:
$token = Tools::getValue('token');
if (empty($token) || !Tools::validateToken($token)) {
    die('Invalid token');
}
```

### 4. Authentication & Authorization

**Ověr že je uživatel přihlášen:**
```php
if (!$this->context->customer->isLogged()) {
    Tools::redirect('index.php?controller=authentication');
}
```

**Ověr oprávnění v admin:**
```php
// AdminController automaticky ověřuje:
public function init() {
    parent::init(); // Kontroluje práva
    if (!$this->access) {
        die('Access denied');
    }
}
```

## Bezpečné Psaní Kódu

### Input Validation

```php
// Validuj všechny vstupy
$email = Tools::getValue('email');
if (!Validate::isEmail($email)) {
    $errors[] = 'Invalid email';
}

$quantity = (int)Tools::getValue('quantity');
if ($quantity < 1 || $quantity > 1000) {
    $errors[] = 'Invalid quantity';
}

// Dostupné validátory
Validate::isInt();
Validate::isFloat();
Validate::isEmail();
Validate::isBool();
Validate::isUrl();
Validate::isGenericName();
Validate::isCleanHtml();
```

### Output Escaping

```php
// PHP - vždycky escape výstupy:
echo htmlspecialchars($user_input);
echo strip_tags($html_content);

// Twig - automatické escaping:
{{ variable }}           {# Escaped by default #}
{{ variable|raw }}      {# Raw HTML - BE CAREFUL #}

// Smarty (PS 1.7):
{$variable|escape:'html':'UTF-8'}
{$variable|escape:'javascript'}
{$variable|escape:'url'}
```

### Database Access

```php
// Vždycky používej prepared statements:
Db::getInstance()->execute(
    "INSERT INTO product (name, price) VALUES (?, ?)",
    [$name, $price]
);

// Nebo klíčové vstupy:
Db::getInstance()->insert('product', [
    'name' => $name,
    'price' => $price,
    'date_add' => date('Y-m-d H:i:s'),
]);

// NIKDY toto:
Db::getInstance()->query("INSERT INTO product VALUES ($name, $price)");
```

## SSL/HTTPS

```php
// Vybivej HTTPS v admin a checkout:
if (!Tools::usingSecureMode()) {
    if (Configuration::get('PS_SSL_ENABLED')) {
        Tools::redirect('https://...');
    }
}
```

Config:
```
PS_SSL_ENABLED = 1
PS_SSL_ENABLED_EVERYWHERE = 1  // HTTPS všude
```

## File Upload Security

```php
// NIKDY nedůvěřuj extension
if ($_FILES['image']['name']) {
    $filename = $_FILES['image']['name'];
    // NEBEZPEČNĚ: přijmout .php soubor se jménem .jpg
}

// BEZPEČNĚ:
public function uploadImage($file)
{
    // Ověř MIME type
    if (!in_array($file['type'], ['image/jpeg', 'image/png'])) {
        return false;
    }
    
    // Ověř skrz getimagesize (kontroluje obsah, ne extension)
    if (!getimagesize($file['tmp_name'])) {
        return false;
    }
    
    // Přejmenuj na bezpečné jméno
    $new_name = uniqid() . '.jpg';
    move_uploaded_file($file['tmp_name'], __DIR__ . '/uploads/' . $new_name);
    
    return $new_name;
}
```

## Password Security

```php
// Hashování hesel
$password = 'user_password';
$hashed = Tools::hash('sha1', $password);  // PS 1.7

// PS 8.x - lépe
$hashed = password_hash($password, PASSWORD_BCRYPT);
if (password_verify($password, $hashed)) {
    // Heslo je správné
}
```

## Common Security Issues v Modulech

### Problém: Global Variables
```php
// NEBEZPEČNĚ - global state
global $_GET, $_POST;
// Třetí party kód může upravit tyto vars!
```

### Řešení: Používej Context
```php
// BEZPEČNĚ
$id = (int)Tools::getValue('id');
$email = Tools::getValue('email');
```

### Problém: No Access Control
```php
// Kontroler bez přístupu kontroly
class MyController extends FrontController {
    public function deleteProduct() {
        // Kde je autentizace?!
    }
}
```

### Řešení: Ověř přístup
```php
public function deleteProduct() {
    if (!$this->context->customer->isLogged()) {
        die('Access denied');
    }
    // ... smaž produkt
}
```

## Bezpečnostní Audit Checklist

- [ ] SQL injection - všechny databázové dotazy
- [ ] XSS - všechny výstupy v templaty
- [ ] CSRF - všechny admin formuláře mají token?
- [ ] Authentication - uživatelé ověřeni?
- [ ] Authorization - oprávnění zkontrolována?
- [ ] File uploads - validovány?
- [ ] SSL/HTTPS - zapnuto na produkci?
- [ ] Error messages - neodhalizují info o systému?
- [ ] Sensititvní data - nejsou v logu?
- [ ] Dependencies - všechny updatované?

## Bezpečnostní Best Practices

1. **Validuj vše** - input, file types, domains
2. **Escapuj vše** - všechny výstupy
3. **Hashuj hesla** - nikdy plaintext
4. **Używaj HTTPS** - vždy
5. **Monitoruj logy** - hledej podezřelou aktivitu
6. **Keep updated** - PS, PHP, modules
7. **Restricted access** - minimálně potřebná práva
8. **Security headers** - Content-Security-Policy, X-Frame-Options
9. **Rate limiting** - zabráň brute-force
10. **2FA** - pro admin panel

## Otázky k Pohovoru

- Jak se chráníš proti SQL injection?
- Jaký je rozdíl mezi XSS a CSRF?
- Jak se ověřuje CSRF token v admin?
- Jak by ses zachoval s file uploadem?
- Jak se hashují hesla v PS?
- Co je Context object a proč je bezpečnější?
- Jaké výstupy se musí escapovat?
- Jak se nastavuje HTTPS?
- Co jsou security headers?
- Jak by jsi auditoval modul na bezpečnost?
