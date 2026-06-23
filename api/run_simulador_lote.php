<?php
// api/run_simulador_lote.php
header('Content-Type: application/json');

$inputJSON = file_get_contents('php://input');

if (!$inputJSON) {
    echo json_encode(['status' => 'error', 'message' => 'Nenhum dado JSON recebido.']);
    exit;
}

$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
$script = dirname(__DIR__) . '/python_scripts/simulador_lote.py';

// Usar proc_open para passar dados pesados via STDIN
$descriptorspec = array(
   0 => array("pipe", "r"),  // stdin é um pipe de onde o processo vai ler
   1 => array("pipe", "w"),  // stdout é um pipe de onde a gente vai ler
   2 => array("pipe", "w")   // stderr
);

$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($script);
$process = proc_open($cmd, $descriptorspec, $pipes);

if (is_resource($process)) {
    // Envia o JSON pro Python
    fwrite($pipes[0], $inputJSON);
    fclose($pipes[0]);

    // Le a resposta
    $output = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    
    // Le possiveis erros
    $erros = stream_get_contents($pipes[2]);
    fclose($pipes[2]);

    proc_close($process);
    
    if (!$output) {
        echo json_encode(['status' => 'error', 'message' => 'Nenhuma resposta do motor em lote.', 'debug' => $erros]);
        exit;
    }
    
    echo $output;
} else {
    echo json_encode(['status' => 'error', 'message' => 'Falha ao iniciar o processo Python.']);
}
