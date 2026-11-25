<?php
require_once __DIR__ . '/import-lib.php';

/**
 * Very cheap front-page import check.
 * - Only scans /import for *.zip.
 * - If there is no ZIP, it returns immediately.
 * - Uses a lock so two simultaneous visitors cannot import the same package.
 * - Successfully imported ZIPs are renamed to *.imported-YYYYmmddHHMMSS.
 * - Failed ZIPs remain in place so they can be inspected/retried.
 */
function auto_import_pending_packages(): array {
    if (!is_dir(IMPORT_DIR)) {
        @mkdir(IMPORT_DIR, 0775, true);
    }

    $packages = glob(IMPORT_DIR . '/*.zip') ?: [];
    if (!$packages) {
        return ['published' => [], 'errors' => []];
    }

    $lockPath = IMPORT_DIR . '/.import.lock';
    $lock = @fopen($lockPath, 'c');
    if (!$lock) {
        return ['published' => [], 'errors' => ['lock' => 'Nelze otevřít importní zámek.']];
    }

    if (!flock($lock, LOCK_EX | LOCK_NB)) {
        fclose($lock);
        return ['published' => [], 'errors' => []];
    }

    $published = [];
    $errors = [];

    try {
        foreach ($packages as $file) {
            try {
                $issue = import_package($file);
                $published[] = $issue['id'];
                @rename($file, $file . '.imported-' . date('YmdHis'));
            } catch (Throwable $e) {
                $errors[basename($file)] = $e->getMessage();
            }
        }
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }

    return ['published' => $published, 'errors' => $errors];
}
