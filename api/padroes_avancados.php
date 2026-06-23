<?php
// api/padroes_avancados.php
header('Content-Type: application/json');

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/analise_padroes.py';

$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script) . ' 2>&1';
$output = shell_exec($cmd);

if (!$output) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta do motor de análise de padrões.']);
    exit;
}

echo $output;
