<?php
header('Content-Type: application/json');

ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $limit = isset($_GET['limit']) ? $_GET['limit'] : '100';
    
    $pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
    $pythonScript = dirname(__DIR__) . '/python_scripts/painel_inteligente.py';
    
    $cmd = escapeshellcmd($pythonExe) . ' ' . escapeshellarg($pythonScript) . ' ' . escapeshellarg($limit);
    $output = shell_exec($cmd . ' 2>&1');
    
    if ($output === null) {
        throw new Exception("Erro ao executar motor inteligente.");
    }
    
    // Tentamos decodificar apenas o JSON
    // Caso haja avisos no output, pegamos da primeira chave '{'
    $jsonStart = strpos($output, '{');
    if ($jsonStart !== false) {
        $jsonStr = substr($output, $jsonStart);
        $result = json_decode($jsonStr, true);
        if ($result) {
            echo json_encode($result);
            exit;
        }
    }
    
    throw new Exception("Erro ao decodificar a resposta da IA: " . $output);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        "status" => "error",
        "message" => $e->getMessage()
    ]);
}
?>
