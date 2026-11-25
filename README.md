# DigiNoviny

Projekt pro zpracování městských novin z PDF, přípravu digitálních článků a jejich publikaci do veřejného webového archivu.

Repozitář obsahuje dvě historicky oddělené části projektu. Nejde zatím o jednu hotovou online aplikaci.

## Struktura repozitáře

- `desktop/` – lokálně spouštěná aplikace v Pythonu. Obsahuje FastAPI aplikaci, HTML šablony, CSS, zpracování PDF, návrhy článků, kontrolu obsahu a export publikačního ZIP balíčku.
- `web/` – PHP webová část. Obsahuje veřejný archiv, zobrazení vydání a článků, administraci a API pro import a publikaci balíčků.
- `.gitignore` – vyloučení lokálních dat, cache a citlivé konfigurace.

## Desktopová část

Hlavní vstupní soubor: `desktop/app/main.py`

Použité technologie podle zdrojového kódu:
- Python
- FastAPI
- PyMuPDF (knihovna `fitz`) pro čtení a vykreslování PDF
- Jinja2 šablony
- Requests pro HTTPS publikaci
- Tesseract OCR s českým jazykovým modelem pro PDF, u kterých je textová vrstva nepoužitelná

Aplikace ukládá pracovní vydání jako JSON do `desktop/data/issues/`, nahraná PDF do `desktop/uploads/` a generované stránky a exporty do `desktop/generated/`.

Hlavní funkce nalezené ve zdrojovém kódu:
- nahrání PDF a kontrola kvality jeho textové vrstvy
- extrakce textových bloků a obrazových oblastí
- OCR při vyhodnocení poškozené textové vrstvy
- návrhy článků a odhad kategorií
- čištění textu včetně spojování slov rozdělených na konci řádku
- editace, ukládání a validace článků
- export vydání do ZIP balíčku
- odeslání balíčku na web přes HTTPS

Spuštění a instalace jsou popsány v `desktop/README.md`, `desktop/requirements.txt` a `desktop/run.bat`. Konfigurace publikování se připravuje podle `desktop/publish-settings.example.json`; skutečný soubor s tokenem se do GitHubu nesmí nahrávat.

## Webová část

Hlavní veřejné stránky jsou v PHP:
- `web/index.php` – veřejný archiv
- `web/issue.php` – zobrazení vydání
- `web/article.php` – zobrazení článku
- `web/search.php`, `web/stats.php`, `web/track.php` – další funkce webu
- `web/admin/index.php` – administrace
- `web/api/` – importní a publikační API

Publikační endpoint `web/api/publish.php` přijímá ZIP přes HTTPS a ověřuje hlavičku `X-Publish-Token` (případně POST parametr `token`). Importní knihovna `web/api/import-lib.php` očekává v ZIPu soubor `manifest.json` s formátem:

```text
skutec-diginoviny-package-v2
```

Import pracuje s články, médii a PDF z balíčku a ukládá vydání do datové struktury webu.

Webová část je připravena pro PHP hosting. Konkrétní požadavky na PHP rozšíření a limity hostingu je nutné ověřit při nasazení. Importní kód výslovně vyžaduje rozšíření PHP `ZipArchive`.

## Vztah obou částí

Současný publikační tok ve zdrojovém kódu:

1. Desktop zpracuje PDF a připraví články.
2. Desktop vytvoří ZIP s `manifest.json`, PDF a soubory médií.
3. Desktop odešle ZIP přes HTTPS na `web/api/publish.php`.
4. Web ověří publikační token a formát balíčku.
5. Web importuje vydání do veřejného archivu.

Formát `skutec-diginoviny-package-v2` je důležitá integrační hranice. Při budoucích úpravách je nutné zachovat zpětnou kompatibilitu, pokud nebude výslovně připraven a otestován migrační postup.

## Cílový směr vývoje

Cílem projektu je postupně vytvořit jednotnou online platformu pro více měst:
- společné přihlášení a oddělené prostředí jednotlivých měst
- role superadministrátor, administrátor města a redaktor
- jednotná online administrace a editor
- konfigurovatelný vzhled každého města
- nahrávání PDF, rozpoznávání článků, editace, schvalování a publikace
- zachování veřejného archivu a stávajícího publikačního formátu, pokud to technická analýza potvrdí

Předpokládaným hostingovým prostředím je současný webhosting Endora s PHP a MySQL. Python/FastAPI na tomto sdíleném hostingu nelze provozovat, proto nelze současnou desktopovou aplikaci pouze přesunout na Endoru. Je nutné navrhnout, které funkce zpracování PDF a OCR lze realizovat v prohlížeči nebo jiným kompatibilním způsobem.

## Známé body k technickému prověření

Tento seznam je výchozí kontrolní seznam, nikoliv potvrzení, že jsou všechny body již opravené:

- Prověřit zabezpečení přístupu do současné PHP administrace a API.
- Prověřit ukládání a správu tajných údajů mimo verzovaný repozitář.
- V desktopovém publikačním kódu je volba TLS ověřování certifikátu nastavena přes `verify=bool(cfg.get("verify_ssl", False))`. Pro produkční použití má být ověřování certifikátu zapnuté.
- V desktopovém zdrojovém kódu zůstaly také starší FTP pomocné funkce; ověřit, zda jsou ještě potřebné, nebo je odstranit.
- Prověřit limity Endory pro velikost uploadu, dobu běhu PHP, paměť, `ZipArchive` a zápis do datových adresářů.
- Prověřit ochranu importních, datových a upload adresářů proti přímému přístupu.
- Ověřit, zda jsou všechny potřebné fonty Poppins skutečně součástí webových assetů. Současné `web/README.txt` uvádí lokální fonty v `web/assets/fonts/`, ale tato složka v aktuálním repozitáři není.

## Bezpečnost a práce s repozitářem

- Repozitář má být soukromý.
- Nikdy necommitovat `web/config.php`, skutečný `publish-settings.json`, hesla, publikační tokeny, databázové přístupy ani soubory `.env`.
- Pro sdílení používat pouze ukázkové konfigurace bez tajných hodnot.
- Lokální pracovní data, nahraná PDF, vygenerované soubory a cache nepatří do verzovaného repozitáře, pokud nejsou výslovně určeny jako anonymizovaná testovací data.

## Pokyny pro další analýzu

Před zásadními změnami nejprve zmapovat existující funkce a jejich návaznosti. Neprovádět automatický kompletní přepis. Zachovat funkční části, veřejný archiv a kompatibilitu publikačního balíčku, dokud nebude doloženo, proč je změna nutná.

Každou navrženou změnu rozdělit na:
1. co je ve zdrojovém kódu skutečně implementováno,
2. co je pouze dokumentováno nebo zamýšleno,
3. co je potřeba opravit,
4. co je potřeba nově vyvinout,
5. jak bude změna otestována.
