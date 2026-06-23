<?php
// api/run_simulador.php
header('Content-Type: application/json');

$dezenas = isset($_GET['dezenas']) ? $_GET['dezenas'] : '';

if (empty($dezenas)) {
    echo json_encode(['status' => 'error', 'message' => 'Dezenas não informadas.']);
    exit;
}

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/simulador.py';

$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script) . ' ' . escapeshellarg($dezenas) . ' 2>&1';
$output = shell_exec($cmd);

if (!$output) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta do simulador.']);
    exit;
}

echo $output;
