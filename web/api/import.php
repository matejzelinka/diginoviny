<?php
require __DIR__.'/import-lib.php';require_admin();
if(!isset($_FILES['package'])||$_FILES['package']['error']!==UPLOAD_ERR_OK)exit('CHYBA: ZIP se nepodařilo nahrát.');
try{$issue=import_package($_FILES['package']['tmp_name']);header('Location: '.BASE_PATH.'/issue.php?id='.urlencode($issue['id']));exit;}catch(Throwable $e){http_response_code(400);exit('CHYBA: '.$e->getMessage());}
