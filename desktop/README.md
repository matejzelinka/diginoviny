# Skutečské noviny – Desktop V4 HTTPS Publish

Automatická publikace už NEPOUŽÍVÁ FTP.

Desktop:
1. vytvoří ZIP,
2. odešle ho přes HTTPS přímo na web,
3. web ZIP okamžitě importuje a publikuje,
4. desktop dostane potvrzení nebo přesnou chybu serveru.

## Nastavení
Zkopíruj publish-settings.example.json jako publish-settings.json.
Do publish_token vlož stejný tajný řetězec jako PUBLISH_TOKEN v config.php webu.

FTP údaje už v desktopu nejsou potřeba.


## V4.1
- Doplněna chybějící závislost requests do requirements.txt.

## V4.2
- Opraven problém Windows/Python s chybějícím lokálním issuer certifikátem.
- Publikační endpoint může mít vypnutou lokální kontrolu certifikačního řetězce přes verify_ssl=false.
- HTTPS šifrování spojení zůstává použité; tato volba pouze obchází lokální selhání ověření certifikátu v Pythonu.

## V4.3
- Obnovena správná oprava slov rozdělených na konci řádku/bloku.
- Opravuje i případy `objek- tu`, `pří- stupu`, `kan- celářím`.
- Hranice PDF bloků se před čištěním zachovají jako nový řádek.
