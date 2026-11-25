# DigiNoviny GPT – pracovní větev

Tato větev `diginoviny-gpt` je oddělená pracovní linie projektu DigiNoviny určená pro spolupráci s ChatGPT.

## Výchozí stav

- Větev vznikla jako kopie aktuální větve `main` repozitáře `matejzelinka/diginoviny`.
- Obsahuje stejný výchozí kód a dokumentaci včetně `CLAUDE_PROJECT_BRIEF.md` a `docs/SECURITY_REVIEW.md`.
- Změny prováděné v této větvi se automaticky nepromítají do `main`.
- Změny z této větve se nepromítají do větve používané Claudem, pokud je výslovně nesloučíme.

## Pravidla práce

1. ChatGPT pracuje primárně ve větvi `diginoviny-gpt`.
2. Claude pracuje ve své vlastní pracovní větvi nebo ve své dohodnuté linii; nesmí bez domluvy přepisovat práci z této větve.
3. Před každou větší změnou se ověří aktuální obsah souborů a návaznosti.
4. Změny se dělají po malých, kontrolovatelných krocích.
5. Produkční nasazení ani změny v `main` se neprovádějí bez výslovného rozhodnutí uživatele.
6. Tajné údaje, `web/config.php`, publikační tokeny, hesla, lokální uploady a testovací osobní data se do repozitáře neukládají.
7. Před sloučením změn do hlavní větve se provede kontrola rozdílů a testování.

## Hlavní zadání

Řiď se dokumentem `CLAUDE_PROJECT_BRIEF.md`, který popisuje cílový produkt, technická omezení, bezpečnost a požadované fáze práce. Jeho pokyny platí i pro práci v této větvi.
