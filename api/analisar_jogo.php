<?php
header('Content-Type: application/json');

ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $id = isset($_GET['id']) ? (int)$_GET['id'] : 0;
    
    if ($id <= 0) {
        throw new Exception("ID inválido.");
    }
    
    // 1. Busca o jogo salvo
    $stmt = $pdo->prepare("SELECT * FROM jogos_salvos WHERE id = ?");
    $stmt->execute([$id]);
    $jogoSalvo = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if (!$jogoSalvo) {
        throw new Exception("Jogo não encontrado.");
    }
    
    // Decodifica JSONs
    $dezenasBase = json_decode($jogoSalvo['dezenas_base'], true) ?: [];
    $dezenasFixas = json_decode($jogoSalvo['dezenas_fixas'], true) ?: [];
    $volantes = json_decode($jogoSalvo['jogos'], true) ?: [];
    
    // 2. Define o concurso alvo (Se não tiver, pega o mais recente)
    if (!empty($jogoSalvo['concurso_alvo'])) {
        $stmtConcurso = $pdo->prepare("SELECT * FROM concursos WHERE concurso = ?");
        $stmtConcurso->execute([$jogoSalvo['concurso_alvo']]);
    } else {
        $stmtConcurso = $pdo->prepare("SELECT * FROM concursos ORDER BY concurso DESC LIMIT 1");
        $stmtConcurso->execute();
    }
    
    $sorteio = $stmtConcurso->fetch(PDO::FETCH_ASSOC);
    
    if (!$sorteio) {
        throw new Exception("Nenhum concurso encontrado no banco de dados para analisar.");
    }
    
    $concursoSorteado = $sorteio['concurso'];
    
    // Dezenas sorteadas
    $sorteadas = [];
    for ($i = 1; $i <= 15; $i++) {
        $sorteadas[] = (int)$sorteio["b$i"];
    }
    
    // 3. Faz a conferência
    $acertosBase = array_intersect($dezenasBase, $sorteadas);
    $acertosFixas = array_intersect($dezenasFixas, $sorteadas);
    
    $premios = [
        11 => ['qtd' => 0, 'valor' => 7.00],
        12 => ['qtd' => 0, 'valor' => 14.00],
        13 => ['qtd' => 0, 'valor' => 30.00],
        14 => ['qtd' => 0, 'valor' => 1900.00], // estimativa
        15 => ['qtd' => 0, 'valor' => 1500000.00] // estimativa
    ];
    
    $valorTotalGanho = 0;
    $volantesAnalisados = [];
    
    foreach ($volantes as $idx => $volante) {
        $acertos = count(array_intersect($volante, $sorteadas));
        $premio = 0;
        if ($acertos >= 11 && $acertos <= 15) {
            $premios[$acertos]['qtd']++;
            $valorTotalGanho += $premios[$acertos]['valor'];
            $premio = $premios[$acertos]['valor'];
        }
        $volantesAnalisados[] = [
            'jogo' => $idx + 1,
            'acertos' => $acertos,
            'premio' => $premio,
            'numeros' => $volante
        ];
    }
    
    $lucro = $valorTotalGanho - (float)$jogoSalvo['custo'];
    
    // --- Módulo de Diagnóstico Avançado ---
    $payload = json_encode([
        'concurso_alvo' => $concursoSorteado,
        'sorteadas' => $sorteadas,
        'dezenas_base' => $dezenasBase,
        'dezenas_fixas' => $dezenasFixas,
        'lucro' => $lucro,
        'nome_estrategia' => $jogoSalvo['nome_estrategia'],
        'custo' => (float)$jogoSalvo['custo']
    ]);
    
    $pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';
    $pythonScript = dirname(__DIR__) . '/python_scripts/diagnostico_ia.py';
    
    // Save payload to a temporary file to avoid Windows command line escaping issues
    $tempFile = sys_get_temp_dir() . '/payload_' . uniqid() . '.json';
    file_put_contents($tempFile, $payload);
    
    $cmd = escapeshellarg($pythonExe) . " \"$pythonScript\" \"$tempFile\" 2>&1";
    $laudoJson = shell_exec($cmd);
    
    // Clean up
    @unlink($tempFile);
    
    // DEBUG: Write to log
    file_put_contents(dirname(__DIR__) . '/api/debug_laudo.txt', "CMD: $cmd\nOUTPUT: $laudoJson\n", FILE_APPEND);
    
    $laudoIa = [];
    if ($laudoJson) {
        $laudoData = json_decode($laudoJson, true);
        if ($laudoData && isset($laudoData['diagnosticos'])) {
            $laudoIa = $laudoData['diagnosticos'];
        }
    }
    
    echo json_encode([
        'status' => 'success',
        'concurso_analisado' => $concursoSorteado,
        'concurso_alvo_salvo' => $jogoSalvo['concurso_alvo'],
        'nome_estrategia' => $jogoSalvo['nome_estrategia'],
        'sorteadas' => $sorteadas,
        'dezenas_base' => $dezenasBase,
        'dezenas_fixas' => $dezenasFixas,
        'acertos_base' => count($acertosBase),
        'acertos_fixas' => count($acertosFixas),
        'total_base' => count($dezenasBase),
        'total_fixas' => count($dezenasFixas),
        'premios' => $premios,
        'valor_ganho' => $valorTotalGanho,
        'custo' => (float)$jogoSalvo['custo'],
        'lucro' => $lucro,
        'volantes_analisados' => $volantesAnalisados,
        'diagnosticos_ia' => $laudoIa
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
