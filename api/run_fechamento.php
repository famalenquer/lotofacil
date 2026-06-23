<?php
// api/run_fechamento.php
error_reporting(0);
@ini_set('display_errors', 0);
header('Content-Type: application/json');

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/fechamento.py';

$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script) . ' 2>&1';
$output = shell_exec($cmd);

if (!$output) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta do motor de fechamento.']);
    exit;
}

// Em caso de warnings do Python, vamos extrair apenas o JSON
$jsonStart = strpos($output, '{');
if ($jsonStart !== false) {
    $output = substr($output, $jsonStart);
}

echo $output;
