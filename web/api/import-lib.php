<?php
require_once dirname(__DIR__).'/config.php';
function import_package(string $zipPath): array {
  if(!class_exists('ZipArchive'))throw new RuntimeException('Hosting nemá ZipArchive.');
  $zip=new ZipArchive();if($zip->open($zipPath)!==true)throw new RuntimeException('Neplatný ZIP.');
  if($zip->locateName('manifest.json')===false){$zip->close();throw new RuntimeException('Chybí manifest.json.');}
  $m=json_decode((string)$zip->getFromName('manifest.json'),true);
  if(($m['format']??'')!=='skutec-diginoviny-package-v2'){$zip->close();throw new RuntimeException('Neznámý formát balíčku.');}
  $id=$m['id']??'';if(!preg_match('/^\d{4}-\d{2}$/',$id)){$zip->close();throw new RuntimeException('Neplatné ID.');}
  $target=ISSUE_ASSET_DIR.'/'.$id;
  if(is_dir($target)){$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($target,FilesystemIterator::SKIP_DOTS),RecursiveIteratorIterator::CHILD_FIRST);foreach($it as $f){$f->isDir()?rmdir($f->getPathname()):unlink($f->getPathname());}rmdir($target);}
  mkdir($target.'/media',0775,true);$articles=$m['articles']??[];
  foreach($articles as &$a){$safe=[];foreach($a['media']??[] as $media){$src=$media['src']??'';if(!preg_match('#^media/[A-Za-z0-9._-]+$#',$src))continue;$data=$zip->getFromName($src);if($data===false)continue;$name=basename($src);file_put_contents($target.'/media/'.$name,$data);$media['src']='issues/'.$id.'/media/'.$name;$safe[]=$media;}$a['media']=$safe;}unset($a);
  $pdfRel=null;$pdf=$m['pdf']??'';if($pdf&&preg_match('/^[A-Za-z0-9._-]+\.pdf$/i',$pdf)){$data=$zip->getFromName($pdf);if($data!==false){file_put_contents($target.'/'.$pdf,$data);$pdfRel='issues/'.$id.'/'.$pdf;}}
  $zip->close();$issue=['id'=>$id,'month'=>(int)$m['month'],'year'=>(int)$m['year'],'pdf'=>$pdfRel,'articles'=>$articles,'published'=>true,'importedAt'=>date(DATE_ATOM)];save_issue($issue);return $issue;
}
