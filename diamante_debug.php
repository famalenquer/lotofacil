<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
$pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
$stmt = $pdo->query("SELECT * FROM jogos_salvos WHERE nome_estrategia LIKE '%diamante%'");
$jogos = $stmt->fetchAll(PDO::FETCH_ASSOC);

$resultados = [];

foreach($jogos as $j) {
    // Pegar o concurso alvo
    if (!empty($j['concurso_alvo'])) {
        $stmtConcurso = $pdo->prepare("SELECT * FROM concursos WHERE concurso = ?");
        $stmtConcurso->execute([$j['concurso_alvo']]);
    } else {
        $stmtConcurso = $pdo->prepare("SELECT * FROM concursos ORDER BY concurso DESC LIMIT 1");
        $stmtConcurso->execute();
    }
    
    $sorteio = $stmtConcurso->fetch(PDO::FETCH_ASSOC);
    if (!$sorteio) continue;

    $sorteadas = [];
    for ($i = 1; $i <= 15; $i++) {
        $sorteadas[] = (int)$sorteio["b$i"];
    }

    $dezenasBase = json_decode($j['dezenas_base'], true) ?: [];
    $dezenasFixas = json_decode($j['dezenas_fixas'], true) ?: [];

    $acertosBase = count(array_intersect($dezenasBase, $sorteadas));
    $acertosFixas = count(array_intersect($dezenasFixas, $sorteadas));

    $resultados[] = [
        'id' => $j['id'],
        'nome' => $j['nome_estrategia'],
        'concurso' => $sorteio['concurso'],
        'sorteadas' => $sorteadas,
        'base' => $dezenasBase,
        'fixas' => $dezenasFixas,
        'acertos_base' => $acertosBase,
        'total_base' => count($dezenasBase),
        'acertos_fixas' => $acertosFixas,
        'total_fixas' => count($dezenasFixas)
    ];
}

echo json_encode($resultados, JSON_PRETTY_PRINT);
?>
