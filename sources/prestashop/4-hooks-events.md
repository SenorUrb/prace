# PrestaShop Hooks a Events

## Hooks vs Events

### Hooks (starší PS 1.7)
Jednosměrná komunikace - modul reaguje na event:

```php
// V modulu
public function hookActionOrderStatusPostUpdate($params)
{
    // Něco se stalo - react
}
```

### Events (novější PS 8.x, Symfony)
Dvousměrná komunikace - event dispatcher:

```php
$dispatcher = $this->container->get('event_dispatcher');
$event = new OrderStatusPostUpdateEvent($order, $newStatus);
$dispatcher->dispatch($event, OrderStatusPostUpdateEvent::class);
```

## Běžné Hooky

### Product Hooks

```php
// Když se vytvoří produkt
public function hookActionProductAdd($params)
{
    $id_product = $params['product']->id;
    // Ulož v cachoe, triggerem API, atd.
}

// Když se upraví produkt
public function hookActionProductUpdate($params)
{
    $id_product = $params['product']->id;
}

// Když se smaže produkt
public function hookActionProductDelete($params)
{
    $id_product = $params['id_product'];
}

// Když se změní cena
public function hookActionProductPriceModification($params)
{
    $id_product = $params['id_product'];
    $new_price = $params['product_price'];
}
```

### Order Hooks

```php
// Nová objednávka
public function hookActionOrderStatusPostUpdate($params)
{
    $id_order = $params['id_order'];
    $new_status = $params['newOrderStatus'];  // Object OrderState
    
    // Pošli notifikaci, Update ERP, atd.
    if ($new_status->id == 2) {  // Zaplaceno
        $this->sendToWarehouse($id_order);
    }
}

// Při vytvoření objednávky
public function hookActionValidateOrder($params)
{
    $order = $params['order'];
    $customer = $params['customer'];
}

// Při zrušení objednávky
public function hookActionOrderCancel($params)
{
    $order = $params['order'];
    // Vrať skladové zásoby, atd.
}
```

### Cart Hooks

```php
// Přidej do košíku
public function hookActionCartUpdateQuantityBefore($params)
{
    // Validuj before update
}

// Smaž z košíku
public function hookActionCartUpdateQuantityAfter($params)
{
    $cart = $params['cart'];
    $product_id = $params['id_product'];
}

// Vyprázdni košík
public function hookActionBeforeCartClear($params)
{
    $cart = $params['cart'];
}
```

### Customer Hooks

```php
// Nový zákazník
public function hookActionCustomerAccountAdd($params)
{
    $customer = $params['newCustomer'];
    // Pošli welcome email, atd.
}

// Upravený zákazník
public function hookActionCustomerAccountUpdate($params)
{
    $customer = $params['customer'];
}

// Přihlášení
public function hookActionFrontControllerSetMedia($params)
{
    // Zavolá se když se přihlásí nebo odhlásí
}
```

### Display Hooks (Front-end)

Tyto hooky renderují obsah v šablonach:

```php
// Nad produktem
public function hookDisplayProductContainer($params)
{
    $product = $params['product'];
    return '<div>Extra info</div>';
}

// Pod produktem
public function hookDisplayProductFooter($params)
{
    return '<div>Related products</div>';
}

// Na homepage
public function hookDisplayHome($params)
{
    return '<div>Welcome banner</div>';
}

// Checkout
public function hookDisplayCheckoutOrder($params)
{
    $cart = $params['cart'];
    return '<div>Payment options</div>';
}

// Potvrzení objednavky
public function hookDisplayOrderConfirmation($params)
{
    $order = $params['order'];
    return '<div>Thank you!</div>';
}
```

## Custom Hooks

Když standardní hooky nestačí, vytvoř si vlastní:

```php
// Zaregistruj v modulu
public function install()
{
    $this->registerHook('displayMyCustomLocation');
    return parent::install();
}

// Zavolej v kódu
$hook_output = Hook::exec(
    'displayMyCustomLocation',
    ['product' => $product]
);

// V šablone (Twig)
{{ hook_render('displayMyCustomLocation', {product: product}) }}
```

## Event System (PS 8.x)

Modernější přístup s Symfony Events:

```php
// Vytvořeni event třídy
class OrderStatusPostUpdateEvent extends Event
{
    private Order $order;
    private OrderState $orderState;
    
    public function __construct(Order $order, OrderState $orderState)
    {
        $this->order = $order;
        $this->orderState = $orderState;
    }
    
    public function getOrder(): Order
    {
        return $this->order;
    }
}

// Listener pro event
class OrderNotificationListener
{
    public function onOrderStatusPostUpdate(OrderStatusPostUpdateEvent $event)
    {
        $order = $event->getOrder();
        // Pošli notifikaci
    }
}

// Registrace
services:
  module.listener.order:
    class: Module\Listener\OrderNotificationListener
    tags:
      - { name: kernel.event_listener, event: PostUpdate, method: onOrderStatusPostUpdate }
```

## Hook s Return Values

```php
// Všechny module vraťují output
public function hookDisplayProductContainer($params)
{
    $output = '';
    $output .= '<div class="extra-info">';
    $output .= '<h3>Additional Info</h3>';
    $output .= '</div>';
    return $output;
}

// Hook Dispatcher slučuje všechny outputy
Hook::exec('displayProductContainer', $params);
// Vrátí: div-module1 + div-module2 + div-module3 ... všechny dohromady
```

## Hook Priority

```php
// Některé hooky se zavolají v pořadí

// Seřazeny podle `position`
SELECT * FROM hook_module WHERE id_hook = 5 ORDER BY position;
// Module A - position 1 (zavolá se první)
// Module B - position 2
// Module C - position 3
```

## Debugging Hooks

```php
// V module loguj
public function hookActionOrderStatusPostUpdate($params)
{
    error_log('Hook called with: ' . json_encode($params));
    
    // nebo
    PrestaShopLogger::addLog('Order updated', 1, null, 'Order', $id_order);
}

// Vidíš v admin: System > Logs > Errors
```

## Common Hook Patterns

### Pattern 1: Cache Invalidation
```php
public function hookActionProductUpdate($params)
{
    Cache::clean('product_' . $params['product']->id);
}
```

### Pattern 2: External API Sync
```php
public function hookActionOrderStatusPostUpdate($params)
{
    $order = new Order($params['id_order']);
    if ($params['newOrderStatus']->id == 2) {  // Zaplaceno
        $this->syncToERP($order);
    }
}
```

### Pattern 3: Email Notification
```php
public function hookActionCustomerAccountAdd($params)
{
    Mail::Send(
        1,
        'welcome',
        'Welcome!',
        ['{firstname}' => $params['newCustomer']->firstname],
        $params['newCustomer']->email
    );
}
```

## Otázky k Pohovoru

- Jaký je rozdíl mezi Hooks a Events?
- Jaké jsou nejčastější hooky?
- Jak se zaregistruje hook v modulu?
- Jak se zavolá custom hook?
- Co je Display hook a co Action hook?
- Jak se debuguje hook?
- Jaké je pořadí zavolání hooků?
- Jak se syncuje s externí API přes hook?
- Jak se invaliduje cache když se změní produkt?
- Jaké jsou best practices pro hooky?
