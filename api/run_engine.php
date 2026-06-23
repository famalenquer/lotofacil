<?php
// api/run_engine.php
header('Content-Type: application/json');

$qtd = 3;
$tamanho = 15;

// Tenta pegar do POST JSON se houver
$inputJSON = file_get_contents('php://input');
$input = json_decode($inputJSON, TRUE);

if (isset($input['qtd'])) {
    $qtd = intval($input['qtd']);
}
if (isset($input['tamanho'])) {
    $tamanho = intval($input['tamanho']);
}

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/engine_preditivo.py';

// Passa qtd e tamanho como argumentos
$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script) . ' ' . escapeshellarg($qtd) . ' ' . escapeshellarg($tamanho) . ' 2>&1';
$output = shell_exec($cmd);

if (!$output) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta do motor de IA.']);
    exit;
}

echo $output;
