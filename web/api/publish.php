<?php
require __DIR__.'/import-lib.php';

header('Content-Type: application/json; charset=utf-8');

$token = (string)($_SERVER['HTTP_X_PUBLISH_TOKEN'] ?? $_POST['token'] ?? '');
if (!hash_equals(PUBLISH_TOKEN, $token)) {
    http_response_code(403);
    echo json_encode(['ok'=>false,'error'=>'Neplatný publikační token.'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (!isset($_FILES['package'])) {
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>'Chybí balíček package.'], JSON_UNESCAPED_UNICODE);
    exit;
}

$uploadError = (int)$_FILES['package']['error'];
if ($uploadError !== UPLOAD_ERR_OK) {
    $map = [
      UPLOAD_ERR_INI_SIZE=>'ZIP je větší než upload_max_filesize na serveru.',
      UPLOAD_ERR_FORM_SIZE=>'ZIP je příliš velký.',
      UPLOAD_ERR_PARTIAL=>'ZIP byl nahrán jen částečně.',
      UPLOAD_ERR_NO_FILE=>'Nebyl nahrán žádný ZIP.',
      UPLOAD_ERR_NO_TMP_DIR=>'Server nemá dočasnou složku.',
      UPLOAD_ERR_CANT_WRITE=>'Server nemůže zapsat dočasný soubor.',
      UPLOAD_ERR_EXTENSION=>'Upload zastavilo PHP rozšíření.'
    ];
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>$map[$uploadError] ?? ('Upload chyba '.$uploadError)], JSON_UNESCAPED_UNICODE);
    exit;
}

try {
    $issue = import_package($_FILES['package']['tmp_name']);
    echo json_encode([
      'ok'=>true,
      'issue'=>$issue['id'],
      'url'=>BASE_PATH.'/issue.php?id='.rawurlencode($issue['id']),
      'message'=>'Vydání bylo přijato přes HTTPS a okamžitě publikováno.'
    ], JSON_UNESCAPED_UNICODE);
} catch (Throwable $e) {
    http_response_code(400);
    echo json_encode(['ok'=>false,'error'=>$e->getMessage()], JSON_UNESCAPED_UNICODE);
}
