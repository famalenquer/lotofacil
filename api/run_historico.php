<?php
// api/run_historico.php
error_reporting(0);
@ini_set('display_errors', 0);
header('Content-Type: application/json');

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/stats_historicas.py';

$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script) . ' 2>&1';
$output = shell_exec($cmd);

if (!$output) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta.']);
    exit;
}

$jsonStart = strpos($output, '{');
if ($jsonStart !== false) {
    $output = substr($output, $jsonStart);
}

echo $output;
