# Bezpecnostni a technicka kontrola – vychozi audit

Datum kontroly: 25. 11. 2026  
Rozsah: zdrojove soubory aktualne ulozene ve vetvi `main`, zejmena `web/api/publish.php`, `web/api/import.php`, `web/api/import-lib.php`, `web/api/auto-import.php`, `web/admin/index.php` a `web/index.php`.

Toto je staticka kontrola zdrojoveho kodu. Nejde o penetracni test ani kontrolu beziciho hostingu.

## Co je potvrzeno

- `web/config.php` neni soucasti verzovaneho repozitare. PHP soubory jej ale vyzaduji. Produkcni konfigurace proto musi byt na serveru vytvorena samostatne.
- Publikacni endpoint `web/api/publish.php` kontroluje token z hlavicky `X-Publish-Token` nebo z POST parametru a porovnava jej s konstantou `PUBLISH_TOKEN`.
- Import vyzaduje PHP rozsireni `ZipArchive`.
- Import kontroluje pritomnost `manifest.json`, format `skutec-diginoviny-package-v2` a tvar ID vydani `YYYY-MM`.
- Cesty medii a PDF z manifestu prochazeji zakladni validaci nazvu/cesty.
- `web/admin/index.php` pouziva jedno heslo ulozene v konfiguraci a prihlaseni drzi v PHP session.
- `web/index.php` pri nacitani uvodni stranky spousti kontrolu ZIP souboru ve slozce `IMPORT_DIR`.

## Nálezy a doporuceni

### Vysoka priorita – import muze smazat predchozi vydani

V `import-lib.php` se pri existujicim ID vydani nejprve smaze jeho dosavadni adresar. Teprve potom se vytvari nova struktura a ukladaji data. Pokud import nasledne selze, muze byt puvodni vydani poskozene nebo ztracene.

Doporuceni:
- nejprve cely ZIP overit a rozbalit do docasneho adresare,
- validovat manifest, clanky, media a PDF,
- az po uspesne kontrole provest atomickou vymenu adresare,
- pred prepsanim existujiciho vydani vytvorit zalohu nebo vyzadovat explicitni potvrzeni.

### Vysoka priorita – automaticky import z adresare

Funkce `auto_import_pending_packages()` zpracovava vsechny soubory `*.zip` v `IMPORT_DIR` bez vlastni kontroly publikatniho tokenu. Bezpecnost tedy zavisi na tom, kdo muze do teto slozky zapisovat.

Doporuceni:
- zajistit, aby do slozky mohl zapisovat pouze duveryhodny proces/administrator,
- zakazat primy HTTP pristup k importni slozce,
- zvazit vypnuti automatickeho importu nebo jeho nahrazeni autentizovanym administracnim procesem.

### Vysoka priorita – validace ZIP balicku

Aktualni import kontroluje zakladni format a cesty medii, ale ve zdrojovem kodu neni videt limit celkove rozbalene velikosti, poctu souboru ani ochrana proti nadmerne kompresi (ZIP bomb).

Doporuceni:
- stanovit maximalni velikost nahravaneho ZIP,
- omezit pocet souboru a souhrnnou rozbalenou velikost,
- kontrolovat velikost kazde polozky a MIME/typ souboru,
- odmítat duplicitni nebo neocekavane polozky archivu.

### Stredni priorita – administrace

Prihlaseni v `web/admin/index.php` pouziva jedno sdilene heslo. V tomto souboru neni videt omezeni poctu pokusu ani CSRF token u odhlaseni a dalsich POST akci. Obnovu ID session po prihlaseni je potreba overit v `config.php` a funkci `admin_ok()`.

Doporuceni:
- zvazit individualni uzivatele a role,
- doplnit omezeni pokusu o prihlaseni,
- pouzit CSRF ochranu pro vsechny stav meniaci pozadavky,
- po uspesnem prihlaseni regenerovat ID session,
- nastavit bezpecne cookie session (Secure, HttpOnly, SameSite) a HTTPS.

### Stredni priorita – chyby a diagnostika

`publish.php` a `import.php` vraceji uzivateli text vyjimky. Pred produkcnim provozem je vhodne oddelit obecnou chybovou zpravu od interniho logu, aby se neprozrazovaly cesty a technicke detaily serveru.

### Stredni priorita – kontrola konfigurace a SSL

- `web/config.php` musi byt vytvoren pouze na serveru a nesmi obsahovat verejne sdilene pristupove udaje.
- V desktopove publikacni logice je nastaveni TLS overovani rizene volbou `verify_ssl`; pro produkci musi byt zapnute.
- Po jakekoli predchozi expozici skutecneho tokenu nebo hesla je nutne tyto udaje zmenit, nikoli pouze odstranit ze souboru.

## Co nelze z repozitare potvrdit

- Skutecne hodnoty a bezpecnost konfigurace na Endore.
- Prava zapisu a HTTP pristup k adresarum `data`, `issues`, `uploads` a `import`.
- PHP limity, dostupnost `ZipArchive` a nastaveni session.
- Zda je web vynucen pres HTTPS.
- Zda hosting provadi zalohy a jak rychle je lze obnovit.

## Navrhovane poradi oprav

1. Osetrit import tak, aby nikdy nesmazal platne vydani pred uspesnym overenim noveho balicku.
2. Zabezpecit adresar automatickeho importu a omezit moznost vlozeni ciziho ZIP.
3. Doplnit limity a validaci ZIP balicku.
4. Zpevnit prihlaseni, session a CSRF ochranu administrace.
5. Omezit detail chyb vracenych verejnym endpointem.
6. Overit konfiguraci a limity na Endore.

Pred implementaci zmen je nutne zachovat kompatibilitu s `skutec-diginoviny-package-v2` a otestovat import na kopii testovaciho vydani.
