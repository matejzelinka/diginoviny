<?php
require __DIR__.'/config.php';$key=(string)($_GET['key']??'');$to=(string)($_GET['to']??'');if($key)track($key);if($to&&str_starts_with($to,'issues/')){header('Location: '.BASE_PATH.'/'.$to);exit;}header('Location: '.BASE_PATH.'/');
