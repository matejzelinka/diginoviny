@echo off
setlocal
cd /d "%~dp0"

echo.
echo === Skutecske noviny - digitalni editor ===
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Vytvarim lokalni Python prostredi...
    py -m venv .venv 2>nul
    if errorlevel 1 python -m venv .venv
    if errorlevel 1 (
        echo CHYBA: Nepodarilo se vytvorit lokalni Python prostredi.
        pause
        exit /b 1
    )
)

echo Kontroluji zavislosti...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Spoustim editor...
start "Skutecske noviny - server" /min ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo Cekam na spusteni editoru...
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 30;$i++){try{$r=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/admin/ -TimeoutSec 2; if($r.StatusCode -ge 200){$ok=$true;break}}catch{}; Start-Sleep -Seconds 1}; if(-not $ok){exit 1}"
if errorlevel 1 (
    echo CHYBA: Editor se do 30 sekund nespustil.
    pause
    exit /b 1
)

start "" "http://127.0.0.1:8000/admin/"
exit /b 0

:error
echo.
echo CHYBA: Instalace zavislosti selhala.
pause
exit /b 1
