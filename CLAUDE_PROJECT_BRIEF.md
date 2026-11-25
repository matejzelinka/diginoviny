# DigiNoviny – hlavní zadání pro Claude

> Účel dokumentu: předat Claudovi kontext projektu, cílový stav, technická omezení a pravidla práce. Tento dokument je zadáním a výchozím bodem, nikoliv potvrzením, že navržená architektura už byla implementována nebo otestována.

## 1. Role a očekávaný způsob práce

Vystupuj jako zkušený softwarový architekt a full-stack vývojář se zkušeností s PHP, MySQL, JavaScriptem/TypeScriptem, zpracováním PDF a redakčními systémy.

Tvým úkolem je pomoci přetvořit stávající DigiNoviny na univerzální online platformu pro digitální městské noviny. Nezačínej bezhlavým přepisem. Nejprve důkladně prozkoumej skutečný obsah repozitáře, ověř současné funkce a závislosti a navrhni postup, který zachová vše, co je funkční a hodnotné.

Pracuj prakticky:
- Prohlédni si celý repozitář včetně zdrojových souborů, nikoliv jen README.
- Při každém technickém závěru rozlišuj mezi ověřeným stavem, předpokladem a návrhem.
- Neodhaduj funkčnost podle názvů souborů nebo dokumentace, ověř ji v kódu.
- Neprováděj rozsáhlé změny bez předchozího vysvětlení jejich dopadu.
- Postupuj po malých, kontrolovatelných etapách. Po každé etapě uveď změněné soubory, důvod změn, testy a známá rizika.
- Pokud něco není jasné, polož jednu konkrétní otázku. Nevymýšlej si odpověď.
- Nevytvářej falešné výsledky testů ani netvrď, že něco funguje, pokud to nebylo skutečně spuštěno a ověřeno.

## 2. Co DigiNoviny řeší

DigiNoviny jsou systém pro převod klasických městských novin ve formátu PDF do přehledné digitální podoby na webu.

Současný projekt obsahuje dvě hlavní části:
1. Desktopovou aplikaci v Pythonu, která zpracovává PDF, rozpoznává text a obrázky, navrhuje články, umožňuje redakční úpravy a připravuje publikační balíček.
2. Webovou část v PHP, která zajišťuje veřejný archiv digitálních novin, zobrazení vydání a článků a import publikovaných dat.

Cílem není pouze modernizovat vzhled současné aplikace. Cílem je vytvořit použitelnou online redakční platformu, kterou mohou využívat různá města bez instalace desktopového programu.

## 3. Cílový produkt

### 3.1 Jedna univerzální platforma pro více měst

- Jedna společná aplikace a jedna přihlašovací stránka.
- Po přihlášení uživatel pracuje v prostředí svého města.
- Města sdílejí stejné funkce a redakční rozhraní.
- Každé město má vlastní konfiguraci: název, logo, barvy, fonty, kategorie, případně další vizuální prvky.
- Data jednotlivých měst musí být bezpečně oddělena. Uživatel jednoho města nesmí získat přístup k datům jiného města.
- Platforma musí umožnit přidávat další města bez kopírování a samostatného vývoje aplikace.

### 3.2 Role a oprávnění

Navrhni a implementuj minimálně tyto role:

- **Superadministrátor** – správa celé platformy, měst, uživatelů, konfigurací a oprávnění.
- **Administrátor města** – správa vydání, uživatelů a nastavení vlastního města v rozsahu přidělených oprávnění.
- **Redaktor** – práce s vydáními a články, úpravy a příprava obsahu podle přidělených oprávnění.

Oprávnění musí být vynucována na serveru/API, nejen skrytím ovládacích prvků v rozhraní.

### 3.3 Redakční proces

Typický pracovní postup:

1. Přihlášení do administrace.
2. Vytvoření nového vydání a nahrání PDF.
3. Zpracování PDF a vytvoření návrhů článků.
4. Zobrazení rozpoznaného obsahu v editoru.
5. Kontrola a úpravy článků, nadpisů, textů, fotografií, popisků a kategorií.
6. Uspořádání článků a fotografií.
7. Kontrola a schválení vydání.
8. Publikace do veřejného archivu.

Je žádoucí co nejvyšší míra automatizace, ale redaktor musí mít možnost vše zkontrolovat a opravit. Systém nesmí potichu publikovat chybný nebo neúplný výsledek.

## 4. Požadavky na editor

Editor je klíčovou částí celého projektu. Musí být skutečně jednodušší a rychlejší než dosavadní pracovní postup, nejen vizuálně modernější.

Požadované funkce:
- Přehled vydání a stránek PDF.
- Náhled původní stránky novin.
- Přehled navržených článků a jejich stavu.
- Editace názvu, perexu, textu, popisků a dalších polí.
- Přiřazování fotografií k článkům.
- Možnost upravit ořez a výřez fotografie.
- Ruční oprava chybných nebo chybějících rozpoznaných částí.
- Kategorie a jejich správa.
- Změna pořadí článků i fotografií, ideálně přetažením.
- Ukládání rozpracované práce bez ztráty změn.
- Jasné rozlišení návrhu, rozpracovaného, schváleného a publikovaného obsahu.
- Validace před publikací a srozumitelné upozornění na chyby.

Při návrhu UX vycházej z práce běžného redaktora, který nechce řešit technické detaily PDF. Upřednostni přehlednost, rychlost, minimum zbytečných kliknutí a možnost pracovat s více články.

Neomezuj se na současný editor. Zhodnoť, které části stávajícího řešení mají hodnotu a které je vhodnější nahradit.

## 5. Veřejná část a archiv

Současná veřejná podoba virtuálních DigiNovin se uživateli líbí a má být zachována jako výchozí vizuální a funkční základ.

- Veřejný archiv musí zůstat přístupný bez přihlášení.
- Zachovej přehled vydání, zobrazení článků a související veřejné funkce, pokud audit potvrdí, že fungují.
- Nová administrace nesmí bezdůvodně rozbít stávající veřejné URL ani publikovaná vydání.
- Pokud je nutná změna datového modelu nebo URL, navrhni migraci a zpětnou kompatibilitu.
- Veřejná část a administrační rozhraní mohou mít odlišný design, ale musí sdílet bezpečný a konzistentní datový základ.

## 6. Technická omezení a preferovaná architektura

### 6.1 Hosting

Projekt má být provozovatelný na současném hostingu Endora Fun.

Známé parametry:
- PHP 8.4.
- MySQL.
- Webhosting podporuje PHP skripty.
- Na sdíleném hostingu nelze provozovat vlastní Python/FastAPI server.
- Uživatel nechce pořizovat další placený server ani být nucen využívat placenou cloudovou backendovou službu.

Tyto limity ber jako zásadní. Nenavrhuj řešení, které vyžaduje trvale běžící Python server, VPS, Docker nebo další placenou službu, pokud k tomu uživatel výslovně nedá souhlas.

Předpokládaná varianta k prověření:
- Frontend: moderní JavaScript/TypeScript, případně React.
- Backend: PHP API.
- Databáze: MySQL.
- PDF náhled a práce se stránkami: PDF.js.
- OCR v prohlížeči: případně Tesseract.js, pokud testy potvrdí přijatelnou rychlost a kvalitu.
- Ukládání souborů: adresáře mimo veřejný přístup nebo bezpečně chráněné úložiště podle možností Endory.

Neber tuto variantu jako definitivní rozhodnutí. Ověř její proveditelnost na Endoře a navrhni nejjednodušší udržitelné řešení. Zvláštní pozornost věnuj limitům PHP, velikosti uploadu, době běhu skriptů, paměti, právům souborů, dostupnosti potřebných PHP rozšíření a výkonu OCR v prohlížeči.

### 6.2 Zpracování PDF a OCR

Stávající desktopová aplikace používá Python a knihovny pro zpracování PDF a OCR. Toto zpracování nelze automaticky přenést na Endoru.

Vyhodnoť:
- Co lze spolehlivě extrahovat přímo z textové vrstvy PDF.
- Kdy je nutné OCR.
- Zda OCR může běžet v prohlížeči uživatele.
- Jak zpracování rozdělit na menší úlohy, aby nedocházelo k timeoutům.
- Jak ukládat průběžné výsledky a umožnit pokračování po přerušení.
- Jak zachovat souřadnice textů a obrázků vůči stránce PDF.
- Jak spojovat textové bloky do článků a přiřazovat fotografie.

Nepředpokládej, že OCR v prohlížeči bude dostatečně rychlé pro každé PDF. Ověř to na skutečných datech.

### 6.3 Datový model a více měst

Navrhni databázový model pro:
- města a jejich konfigurace,
- uživatele a role,
- vazby uživatelů na města,
- vydání,
- stránky PDF,
- články,
- textové bloky,
- obrázky a jejich ořezy,
- kategorie,
- stav zpracování a schvalování,
- historii změn a publikace.

Každý záznam patřící městu musí mít jednoznačnou vazbu na konkrétní město. Přístupová kontrola musí být součástí každého relevantního API endpointu a databázových operací.

## 7. Zachování současné integrace a kompatibility

Současná desktopová aplikace vytváří publikační balíček s formátem:

`skutec-diginoviny-package-v2`

Balíček se posílá přes HTTPS do PHP endpointu `web/api/publish.php`. Ten ověřuje publikační token a předává data do `web/api/import-lib.php`.

Tento formát je důležitá integrační hranice. Než navrhneš jeho změnu:
- Prostuduj jeho skutečnou implementaci.
- Zjisti, které části webu a desktopu na něm závisejí.
- Zachovej kompatibilitu, pokud to není technicky nevhodné.
- Případnou změnu proveď přes verzovaný formát a migrační postup.
- Neodstraňuj současný import ani veřejný archiv bez náhrady a ověřeného migračního plánu.

## 8. Bezpečnost

Bezpečnost je zásadní, protože platforma bude obsluhovat více samostatných měst.

Prostuduj také soubor `docs/SECURITY_REVIEW.md`, který obsahuje předchozí statický audit. Jde o seznam zjištění k ověření a opravě, nikoliv o penetrační test.

Zvláštní pozornost věnuj:
- oddělení dat jednotlivých měst,
- autentizaci a správě relací,
- autorizaci každého API požadavku,
- bezpečnému ukládání hesel,
- CSRF ochraně a omezení pokusů o přihlášení,
- bezpečnému uploadu a rozbalování ZIP/PDF souborů,
- limitům velikosti, počtu a typů souborů,
- ochraně adresářů s daty a soubory,
- validaci vstupů a výstupů,
- ochraně publikačních tokenů a dalších tajných údajů,
- HTTPS a ověřování TLS certifikátů,
- zálohám a obnově dat,
- logování důležitých operací.

Nikdy nevypisuj skutečné tokeny, hesla ani jiné tajné hodnoty do logů, dokumentace, ukázek nebo GitHubu. Soubor `web/config.php` je lokální konfigurační soubor a je vyloučen z GitHubu. Zachovej toto pravidlo. Pro sdílení používej pouze bezpečný vzorový konfigurační soubor bez tajných hodnot.

Před jakýmkoliv mazáním nebo nahrazováním dat musí existovat bezpečný postup, aby selhání importu nezničilo předchozí publikované vydání.

## 9. Skutečná testovací data

K dispozici je skutečné PDF:

- Lokální cesta na počítači uživatele: `C:\Users\Anna\Desktop\Docling\noviny.pdf`
- Vydání: Skutečské noviny č. 11/2026.
- Datum vydání: 2. listopadu 2026.
- Počet stran: 10.
- Velikost: přibližně 19,4 MB.

K dispozici je také Docling JSON:

- Lokální cesta: `C:\Users\Anna\Desktop\Docling\vystup_celkovy\noviny.json`
- Velikost: přibližně 696 kB.
- Hlavní položky: `schema_name`, `version`, `name`, `origin`, `furniture`, `body`, `groups`, `texts`, `pictures`, `tables`, `key_value_items`, `form_items`, `pages`.
- Obsahuje 683 textových prvků, 87 obrazových prvků, 22 skupin, 2 tabulky a 10 stránek.

Důležité:
- PDF a JSON jsou zatím lokálně na počítači uživatele. Nepředpokládej, že jsou součástí GitHub repozitáře.
- Požádej uživatele o jejich bezpečné předání nebo o nahrání do vhodného testovacího umístění, až je budeš skutečně potřebovat.
- Nevkládej automaticky celé noviny do veřejného repozitáře.
- JSON je surový výstup Doclingu, nikoliv hotový seznam článků.
- Počty textových a obrazových prvků nejsou počty článků a fotografií v redakčním smyslu.
- V jedné ukázce textového prvku se objevila hodnota `737/19` a záporné souřadnice bounding boxu. Ověř kvalitu souřadnic a práci s okraji stránky; nepředpokládej, že všechny prvky jsou správné.

Při testování používej skutečné PDF a jeho JSON, aby bylo možné porovnat výsledky s reálným vzhledem novin. Testy musí zahrnovat i ruční opravu chybně rozpoznaného obsahu.

## 10. Dosavadní obsah repozitáře

Repozitář: `matejzelinka/diginoviny`  
Výchozí větev: `main`  
Repozitář je soukromý.

Základní struktura, kterou je nutné ověřit proti aktuálnímu stavu repozitáře:

```text
diginoviny/
├── desktop/
│   ├── app/
│   │   ├── main.py
│   │   ├── static/
│   │   └── templates/
│   ├── requirements.txt
│   ├── README.md
│   └── run.bat
├── web/
│   ├── api/
│   │   ├── auto-import.php
│   │   ├── import-lib.php
│   │   ├── import.php
│   │   └── publish.php
│   ├── admin/
│   ├── assets/
│   ├── index.php
│   ├── issue.php
│   ├── article.php
│   ├── search.php
│   └── stats.php
├── docs/
│   └── SECURITY_REVIEW.md
└── README.md
```

Tento seznam je orientační. Aktuální repozitář je rozhodující.

V repozitáři je také soubor `.gitignore`, který mimo jiné vylučuje konfigurační soubory, virtuální prostředí, uploady a generovaná data. Zachovej ochranu tajných a lokálních souborů.

## 11. Známá technická rizika k ověření

Předchozí statická kontrola upozornila mimo jiné na následující body. Znovu je ověř v aktuálním kódu:

1. Import stejného ID vydání v `import-lib.php` může před dokončením nového importu smazat existující adresář vydání.
2. `auto-import.php` zpracovává ZIP soubory z importního adresáře a jeho ochrana musí být ověřena.
3. Import potřebuje důslednější validaci manifestu, cest, velikostí a počtu rozbalovaných souborů.
4. Admin může používat jedno sdílené heslo; ověř aktuální autentizaci, role, CSRF a ochranu proti hádání hesel.
5. Chybové odpovědi nesmí zveřejňovat interní výjimky a citlivé informace.
6. Desktopový publikační klient má nastavení `verify_ssl` s výchozí hodnotou `False`; ověř a oprav bezpečné ověřování TLS.
7. Ověř dostupnost PHP rozšíření a limity Endory, zejména pro uploady, ZIP a práci se soubory.
8. Ověř ochranu adresářů, ve kterých jsou uložená vydání, uploady a importní balíčky.

Nevydávej tato zjištění za potvrzené aktuální chyby, dokud je znovu neověříš.

## 12. Co nechceme

- Nechceme další placený server ani povinný placený cloudový backend.
- Nechceme zachovat desktopovou aplikaci jako jedinou cestu pro redakční práci.
- Nechceme, aby každé město mělo vlastní kopii aplikace.
- Nechceme pouze kosmetický redesign současného editoru.
- Nechceme ztratit veřejný archiv a existující vydání.
- Nechceme automatické publikování nezkontrolovaných chybných článků.
- Nechceme zbytečně přepisovat ověřené části systému.
- Nechceme ukládat hesla, tokeny ani jiné tajné údaje do repozitáře.
- Nechceme stavět řešení na funkcích, které Endora sdílený hosting neumí provozovat.

## 13. Požadovaný postup práce

### Fáze 1 – audit a pochopení systému

Nejdříve projdi celý repozitář. Vytvoř:
- přehled současné architektury,
- popis skutečného pracovního toku od PDF po veřejné vydání,
- seznam existujících funkcí desktopové a webové části,
- přehled datových formátů a API,
- seznam částí, které lze zachovat,
- seznam částí, které je nutné změnit,
- seznam bezpečnostních a provozních rizik,
- seznam neznámých skutečností, které je nutné ověřit.

Zatím nic zásadního nepřepisuj.

### Fáze 2 – cílová architektura a plán

Navrhni konkrétní architekturu, která poběží na Endoře. U každé technologie uveď:
- proč ji volíš,
- zda ji Endora podporuje,
- jaká má omezení,
- jak bude probíhat nasazení,
- jak bude zajištěna bezpečnost a oddělení měst.

Rozděl implementaci do malých etap a stanov ověřitelné výstupy.

### Fáze 3 – funkční základ online administrace

Nejprve vytvoř bezpečný základ:
- přihlášení a odhlášení,
- role a oprávnění,
- správu měst,
- konfiguraci vzhledu města,
- základní správu uživatelů,
- bezpečné PHP API a databázovou strukturu.

### Fáze 4 – online zpracování vydání

Postupně implementuj:
- založení vydání,
- upload PDF,
- náhled stránek,
- extrakci textu a obrázků,
- OCR podle potřeby,
- ukládání průběžných výsledků,
- vytváření návrhů článků,
- možnost ruční opravy.

### Fáze 5 – redakční editor

Implementuj editor podle požadavků v části 4. Testuj jej na skutečných novinách. Prioritou je rychlá a přehledná práce redaktora.

### Fáze 6 – publikace a kompatibilita

Propoj editor s veřejným archivem. Zachovej existující vydání a URL, pokud možno i současný publikační formát. Ověř celý proces od nahrání PDF až po veřejně dostupný článek.

### Fáze 7 – testy a nasazení

Připrav:
- testovací scénáře pro jednotlivé role,
- test oddělení dat měst,
- test uploadu a chybových stavů,
- test zpracování skutečného PDF,
- test importu a publikace,
- zálohování a obnovu,
- návod na nasazení na Endoru,
- návod pro superadministrátora a administrátory měst.

## 14. První konkrétní úkol pro tebe

Začni pouze Fází 1.

Prostuduj celý aktuální repozitář `matejzelinka/diginoviny`, včetně:
- root README,
- `desktop/`,
- `web/`,
- `docs/SECURITY_REVIEW.md`,
- konfigurace, API, importu a publikačního procesu.

Potom mi předlož přehled současného stavu a doporučený plán. Výslovně odpověz:
1. Co dnes skutečně funguje a kde?
2. Co lze zachovat bez zásadního přepisu?
3. Co musí být přepracováno pro online multi-city provoz?
4. Jaká architektura je reálně proveditelná na Endora Fun s PHP 8.4 a MySQL?
5. Jaké jsou největší technické a bezpečnostní překážky?
6. Jaké konkrétní soubory nebo informace ještě potřebuješ?

**V první fázi nic nemaž, nepřepisuj ani nenasazuj na produkční hosting.** Nejdřív chci vidět audit založený na skutečném kódu a návrh postupu.