<?php
require __DIR__.'/config.php';
$monthNames = [1=>'LEDEN',2=>'ÚNOR',3=>'BŘEZEN',4=>'DUBEN',5=>'KVĚTEN',6=>'ČERVEN',7=>'ČERVENEC',8=>'SRPEN',9=>'ZÁŘÍ',10=>'ŘÍJEN',11=>'LISTOPAD',12=>'PROSINEC'];
require_once __DIR__.'/api/auto-import.php';
$autoImportResult = auto_import_pending_packages();
$issues=[];
foreach (glob(DATA_DIR.'/*.json') ?: [] as $f) {
  $d=json_decode((string)file_get_contents($f),true);
  if (!empty($d['published'])) $issues[]=$d;
}
usort($issues,fn($a,$b)=>strcmp($b['id'],$a['id']));
?><!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="https://www.skutec.cz/favicon.ico"><link rel="shortcut icon" href="https://www.skutec.cz/favicon.ico"><title>Skutečské noviny</title><link rel="stylesheet" href="<?=BASE_PATH?>/assets/style.css?v=20260715-final2"></head><body>
<header class="citybar"><div class="topin"><a class="citybrand" href="https://www.skutec.cz/"><span class="cityidentity"><img src="<?=BASE_PATH?>/assets/logo-skutec.png" alt="Město Skuteč"></span></a><a class="cityback" href="https://www.skutec.cz/">← Zpět na web města</a></div></header><header class="top"><div class="topin"><b>DIGITÁLNÍ SKUTEČSKÉ NOVINY</b><span></span></div></header>
<main class="wrap hero"><div class="eyebrow">Město Skuteč</div><h1>Skutečské<br>noviny</h1><h2>Digitální vydání</h2><form class="searchform" action="<?=BASE_PATH?>/search.php"><input name="q" placeholder="Hledat ve všech Skutečských novinách…"><button class="primary">Hledat</button></form><div class="grid">
<?php foreach($issues as $i): ?><a class="card" href="<?=BASE_PATH?>/issue.php?id=<?=htmlspecialchars($i['id'])?>"><div class="eyebrow">Digitální vydání</div><h2><?=htmlspecialchars($monthNames[(int)($i['month']??0)] ?? '', ENT_QUOTES, 'UTF-8')?></h2><p><?=count($i['articles']??[])?> článků</p><b>Otevřít vydání →</b></a><?php endforeach; ?>
<?php if(!$issues): ?><p>Zatím není publikované žádné vydání.</p><?php endif; ?></div></main><footer class="footer"><div class="topin"><b>Město Skuteč</b><span>Palackého náměstí 133 · 539 73 Skuteč · mesto@skutec.cz</span></div></footer></body></html>