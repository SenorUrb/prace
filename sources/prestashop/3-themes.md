# PrestaShop Themes a Templates

## Theme Struktura

```
themes/mytheme/
├── config/
│   ├── theme-bootstrap.yml    # Theme config (PS 8.x)
│   ├── theme.yml              # Settings
│   └── modules.yml            # Module overrides
├── templates/
│   ├── layout.html.twig       # Main layout
│   ├── checkout/
│   ├── product/
│   ├── page/
│   ├── _partials/
│   └── email/                 # Email templates
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── fonts/
├── modules/                   # Theme overrides pro moduly
│   └── modulename/
│       └── views/templates/
├── translations/              # Jazykové soubory
├── preview.png               # Theme preview
└── README.md
```

## Twig vs Smarty

### Twig (PS 8.x - moderní)
```twig
{# Proměnné #}
{{ variable }}
{{ product.name }}

{# Podmínky #}
{% if user.logged_in %}
  Ahoj {{ user.name }}!
{% endif %}

{# Cykly #}
{% for product in products %}
  <div>{{ product.name }}</div>
{% endfor %}

{# Filtry #}
{{ price | number_format(2) }}
{{ text | truncate(20) }}

{# Makra #}
{% macro button(label) %}
  <button>{{ label }}</button>
{% endmacro %}
```

### Smarty (PS 1.7 - starší)
```smarty
{* Proměnné *}
{$variable}
{$product->name}

{* Podmínky *}
{if $user.logged_in}
  Ahoj {$user.name}!
{/if}

{* Cykly *}
{foreach from=$products item=product}
  <div>{$product->name}</div>
{/foreach}

{* Filtry *}
{$price|number_format:2}
{$text|truncate:20}
```

## Responsive Design

### Bootstrap Integration (PS 1.7+)
```twig
<div class="container">
  <div class="row">
    <div class="col-md-4">
      Sidebar
    </div>
    <div class="col-md-8">
      Content
    </div>
  </div>
</div>
```

### Mobile First
```css
/* Mobile first approach */
.product {
  display: block;
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .product {
    display: inline-block;
    width: 50%;
  }
}

/* Desktop */
@media (min-width: 1200px) {
  .product {
    width: 25%;
  }
}
```

## Asset Management

### CSS a JS přidání

```php
// V controller:
$this->context->controller->addCSS(_PS_CSS_DIR_ . 'custom.css');
$this->context->controller->addJS(_PS_JS_DIR_ . 'custom.js');

// V theme config (PS 8.x):
$this->context->controller->registerStylesheet(
    'custom-css',
    _PS_CSS_DIR_ . 'custom.css'
);
```

### Critical CSS (Performance)

```html
<!-- Inline critical CSS -->
<style>
  /* Critical path styles */
</style>

<!-- Defer non-critical -->
<link rel="preload" href="/css/main.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

## Parent/Child Themes

### Parent Theme
```
themes/mytheme/
├── templates/
├── assets/
└── README.md
```

### Child Theme (Dědí z parent)
```
themes/mytheme-child/
├── config/
│   └── theme.yml     # parent: mytheme
├── templates/        # Přepisuj pouze custom
└── assets/          # Dědí z parent
```

Config child theme:
```yaml
parent: mytheme
name: My Theme Child
```

## Hooks Display

Místa kde se modul obsah zobrazuje v theme:

### Běžné display hooky

```twig
{* Layout *}
{% hook 'displayBeforeBodyClosingTag' %}
{% hook 'displayBeforeHeadClosingTag' %}

{* Produkt *}
{% hook 'displayProductContainer' %}
{% hook 'displayProductButtons' %}
{% hook 'displayProductTabContent' %}

{* Košík *}
{% hook 'displayCartBefore' %}
{% hook 'displayCartAfter' %}

{* Checkout *}
{% hook 'displayCheckoutOrder' %}
{% hook 'displayOrderConfirmation' %}

{* Stránky *}
{% hook 'displayLeftColumn' %}
{% hook 'displayRightColumn' %}
{% hook 'displayContent' %}
```

## Email Templates

```
themes/mytheme/templates/email/
├── layout.html.twig
├── order/
│   ├── order_conf.html.twig    # Potvrzení objednavky
│   ├── new_order.html.twig     # Email na admin
│   └── order_changed.html.twig # Změna statusu
├── payment_error.html.twig
└── customer/
    ├── account.html.twig       # Nový účet
    └── password.html.twig      # Reset hesla
```

Email template příklad:
```twig
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{{ 'Order confirmation'|trans }}</title>
</head>
<body>
  <h1>{{ 'Thank you for your order'|trans }}</h1>
  
  <table>
    <tr>
      <th>{{ 'Product'|trans }}</th>
      <th>{{ 'Qty'|trans }}</th>
      <th>{{ 'Price'|trans }}</th>
    </tr>
    {% for item in order.products %}
    <tr>
      <td>{{ item.name }}</td>
      <td>{{ item.quantity }}</td>
      <td>{{ item.price|number_format }}</td>
    </tr>
    {% endfor %}
  </table>
</body>
</html>
```

## Theme Configuration (PS 8.x)

```yaml
# themes/mytheme/config/theme.yml
name: My Theme
version: 1.0.0
description: My awesome theme
license: AFL-3.0

author:
  name: Martin Urbánek
  email: martin@example.com

homepage: https://example.com

colors:
  - name: primary
    value: '#007bff'
  - name: secondary
    value: '#6c757d'

features:
  - breadcrumbs
  - customer_account
  - contact_us
  - search
  - pagination

```

## Theme Optimization

### Performance
```twig
{# Lazy loading #}
<img loading="lazy" src="{{ product.image }}" alt="{{ product.name }}">

{# Async scripts #}
<script async src="analytics.js"></script>

{# Critical CSS #}
<link rel="preload" href="critical.css" as="style">

{# Defer non-critical #}
<link rel="preload" href="main.css" as="style">
```

### Image Optimization
```php
// Vygeneruj thumbnails
$image = new Image($id_image);
$image->getExistingPathFromLegacy();

// Responsive images
$products = Product::getRandomProduct();
foreach ($products as $product) {
    $image = Image::getCover($product['id_product']);
}
```

## Otázky k Pohovoru

- Jaký je rozdíl mezi Twig a Smarty?
- Jak je struktura theme ve PS?
- Jak se přidávají CSS a JS assety?
- Co jsou display hooky a jak se používají?
- Jak vytvořiš child theme?
- Jak optimalizuješ theme performance?
- Jak vyvíjíš responsive design v PS?
- Jak se overrideují module templates v theme?
- Co je Critical CSS a proč je důležitý?
- Jak se zpracovávají email templates?
