# PrestaShop Modulární Systém

## Co je modul?

Modul je balíček kódu, který přidává nebo mění funkcionalitu PrestaShop:

- Pluginy, rozšíření, add-ony
- Zapnutí/vypnutí bez smazání
- Vlastní business logic
- Komunikuje přes hooky a events

## Struktura Modulu

```
modules/mymodule/
├── mymodule.php          # Hlavní třída modulu
├── config.xml            # Metadata (PS 1.7)
├── config_1_6.xml        # Verze 1.6
├── views/
│   ├── templates/        # Frontend šablony
│   ├── css/
│   └── js/
├── controllers/
│   ├── front/
│   └── admin/
├── classes/              # Model třídy
├── translations/         # Jazykové soubory
├── sql/                  # Database install/uninstall
├── upgrade/              # Upgrade skripty
└── tests/               # Unit testy
```

## Základní Modul - Příklad

```php
<?php
// mymodule/mymodule.php
class MyModule extends Module
{
    public function __construct()
    {
        $this->name = 'mymodule';
        $this->tab = 'front_office_features';
        $this->version = '1.0.0';
        $this->author = 'Martin Urbánek';
        $this->need_instance = 1;
        $this->bootstrap = true;
        
        parent::__construct();
        
        $this->displayName = $this->l('My Awesome Module');
        $this->description = $this->l('Does something awesome');
    }
    
    public function install()
    {
        if (!parent::install()) {
            return false;
        }
        
        // Zaregistruj hooky
        $this->registerHook('displayProductContainer');
        $this->registerHook('actionOrderStatusPostUpdate');
        
        // Vytvoř databázi tabulky
        return $this->createTables();
    }
    
    public function uninstall()
    {
        // Zrus databázi tabulky
        $this->dropTables();
        
        return parent::uninstall();
    }
    
    // Hook implementace
    public function hookDisplayProductContainer($params)
    {
        return 'Extra product info';
    }
}
```

## Hooky - Jak Modul Komunikuje

Hooky jsou "body" kde se modulový kód zavolá automaticky:

```php
// V modulu - zaregistruj hook
$this->registerHook('hookName');

// Implementuj hook metodu
public function hookProductFooter($params)
{
    // Vrať HTML
    return $html;
}
```

### Příklady Hooků

| Hook | Kdy se zavolá | Typ |
|------|---------------|-----|
| `hookDisplayProductContainer` | Na product stránce | Display |
| `hookActionOrderStatusPostUpdate` | Po zmene status objednavky | Action |
| `hookActionProductUpdate` | Po zmene produktu | Action |
| `hookDisplayBeforeBodyClosingTag` | Pred zavrime body tag | Display |
| `hookAddProduct` | Pri vytvoreni produktu | Action |
| `hookCustomerAccount` | Na customer account strance | Display |

### Types of Hooks

**Display Hooks** (zobrazují obsah):
```php
public function hookDisplayProductContainer($params)
{
    return '<div>Dodatečný obsah</div>';
}
```

**Action Hooks** (reagují na akce, vrátí void):
```php
public function hookActionOrderStatusPostUpdate($params)
{
    $order_id = $params['id_order'];
    $new_status = $params['newOrderStatus'];
    // Děláme něco...
}
```

## Module Configuration

### config.xml (PS 1.7)
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<module>
    <name>mymodule</name>
    <displayName><![CDATA[My Module]]></displayName>
    <version><![CDATA[1.0.0]]></version>
    <description><![CDATA[My awesome module description]]></description>
    <author><![CDATA[Martin Urbánek]]></author>
    <tab><![CDATA[front_office_features]]></tab>
    <is_configurable>1</is_configurable>
    <need_instance>1</need_instance>
    <limited_countries></limited_countries>
</module>
```

## Module Configuration Page

Admin stránka pro modul settings:

```php
public function getContent()
{
    $output = '';
    
    // Zpracuj formulář (POST)
    if (Tools::isSubmit('submit' . $this->name)) {
        Configuration::updateValue('MYMODULE_SETTING', Tools::getValue('setting'));
        $output .= $this->displayConfirmation($this->l('Settings saved'));
    }
    
    // Renderi formulář
    return $output . $this->renderForm();
}

protected function renderForm()
{
    $form = [
        'form' => [
            'legend' => ['title' => 'Settings'],
            'input' => [
                [
                    'type' => 'text',
                    'label' => 'Setting',
                    'name' => 'setting',
                    'value' => Configuration::get('MYMODULE_SETTING'),
                ]
            ],
            'submit' => ['title' => 'Save']
        ]
    ];
    
    $helper = new HelperForm();
    return $helper->generateForm([$form]);
}
```

## Module Database

```php
// V install() metodě
private function createTables()
{
    $sql = "CREATE TABLE IF NOT EXISTS `" . _DB_PREFIX_ . "mymodule_data` (
        `id_data` INT AUTO_INCREMENT PRIMARY KEY,
        `id_product` INT NOT NULL,
        `value` VARCHAR(255),
        `date_add` DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;";
    
    return Db::getInstance()->execute($sql);
}

// V uninstall() metodě
private function dropTables()
{
    return Db::getInstance()->execute(
        "DROP TABLE IF EXISTS `" . _DB_PREFIX_ . "mymodule_data`"
    );
}
```

## Module Upgrade

Verze upgrade skripty v `/upgrade/`:

```
upgrade/
├── install-1.0.0.php
├── install-1.1.0.php
└── install-2.0.0.php
```

```php
// upgrade/install-1.1.0.php
if (!defined('_PS_VERSION_')) {
    exit;
}

function upgrade_module_1_1_0($module)
{
    // Přidej nový sloupec
    Db::getInstance()->execute("
        ALTER TABLE `" . _DB_PREFIX_ . "mymodule_data`
        ADD COLUMN `new_field` VARCHAR(255)
    ");
    
    return true;
}
```

## Module Best Practices

### Do ✓
- Použít `_DB_PREFIX_` pro bezpečnou tabulku
- Registrovat hooky v install()
- Validovat všechny vstupy
- Usar configuration pro settings
- Psát přeložitelné texty (l() metoda)
- Použít version compare pro upgrade
- Testovat na více verzí PS

### Ne-dělej ✗
- Neukládej config přímo do souborů
- Nepoužívej SQL injections
- Nepředpokládej třídy bez kontroly
- Neměň jádro PS souborů
- Nepoužívej globální proměnné

## Publikace Modulu

1. **Testování**
   - Múltiple PS verzí
   - Múltiple browser
   - SQL injection test
   - XSS test

2. **Dokumentace**
   - README
   - Installation guide
   - Configuration guide
   - Changelog

3. **Distribution**
   - PrestaShop Addons Marketplace
   - GitHub
   - Vlastní web

## Otázky k Pohovoru

- Jak vytvořiš nový modul od nuly?
- Jaký je rozdíl mezi Display a Action hooky?
- Jak registruješ a implementuješ hook?
- Jak uložíš modul konfiguraci?
- Jak se řeší modul upgrade?
- Jaké bezpečnostní rizika mají moduly?
- Jak debuggeš modul?
- Jak publikuješ modul na Addons Marketplace?
- Co je `_DB_PREFIX_` a proč je důležitý?
