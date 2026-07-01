<?php
header('Content-Type: application/json');

ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $input = file_get_contents("php://input");
    $data = json_decode($input, true);
    
    if (!$data || empty($data['estrategia'])) {
        throw new Exception("Dados inválidos. Estratégia não definida.");
    }
    
    $estrategia = $data['estrategia'];
    $dezenasBase = $data['dezenas_base'] ?? [];
    $dezenasFixas = $data['dezenas_fixas'] ?? [];
    
    // Validar se tem o numero correto para a estrategia
    if ($estrategia === 'normal' || $estrategia === 'economico') {
        if (count($dezenasBase) !== 18 || count($dezenasFixas) !== 0) {
            throw new Exception("Estratégia exige exatamente 18 dezenas variáveis.");
        }
    } elseif ($estrategia === 'diamante_economico') {
        if (count($dezenasBase) !== 16 || count($dezenasFixas) !== 3) {
            throw new Exception("Diamante Econômico exige 3 fixas e 16 variáveis.");
        }
    } elseif ($estrategia === 'diamante_supremo') {
        if (count($dezenasBase) !== 17 || count($dezenasFixas) !== 3) {
            throw new Exception("Diamante Supremo exige 3 fixas e 17 variáveis.");
        }
    } else {
        throw new Exception("Estratégia desconhecida.");
    }
    
    // Montar payload para Python
    $payloadJson = json_encode([
        'estrategia' => $estrategia,
        'dezenas_base' => $dezenasBase,
        'dezenas_fixas' => $dezenasFixas
    ]);
    
    $pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
    $pythonScript = dirname(__DIR__) . '/python_scripts/fechamento_manual.py';
    
    // Save to temp file
    $tempFile = sys_get_temp_dir() . '/payload_manual_' . uniqid() . '.json';
    file_put_contents($tempFile, $payloadJson);
    
    $cmd = escapeshellcmd($pythonExe) . ' ' . escapeshellarg($pythonScript) . ' ' . escapeshellarg($tempFile);
    $output = shell_exec($cmd . ' 2>&1');
    
    unlink($tempFile);
    
    if ($output === null) {
        throw new Exception("Erro ao executar script de otimização matemática.");
    }
    
    $result = json_decode($output, true);
    if (!$result) {
        throw new Exception("Erro ao decodificar a resposta matemática: " . $output);
    }
    
    echo json_encode($result);

} catch (Exception $e) {
    echo json_encode([
        "status" => "error",
        "message" => $e->getMessage()
    ]);
}
