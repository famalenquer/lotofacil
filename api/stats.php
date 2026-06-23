<?php
// api/stats.php
header('Content-Type: application/json');
require_once '../config/db.php';

$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 100;

try {
    // 1. Busca os últimos N concursos
    $stmt = $pdo->prepare("
        SELECT c.*, e.qtd_pares, e.qtd_impares, e.qtd_primos, e.soma_dezenas, e.repetidas_anterior 
        FROM concursos c
        LEFT JOIN estatisticas_concurso e ON c.concurso = e.concurso_id
        ORDER BY c.concurso DESC 
        LIMIT :limit
    ");
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $resultados = $stmt->fetchAll();

    if (!$resultados) {
        echo json_encode(['error' => 'Nenhum dado encontrado']);
        exit;
    }

    // Processamento Estatístico
    $frequencia_dezenas = array_fill(1, 25, 0);
    $somas = [];
    $pares_impares_padrao = [];
    $concursos_labels = [];
    $atraso_dezenas = array_fill(1, 25, 0);
    $dezenas_achadas_atraso = array_fill(1, 25, false);

    // Como $resultados está em ordem DESC (do mais novo pro mais velho), 
    // é perfeito para calcular o atraso (quantos concursos sem sair).
    
    foreach ($resultados as $row) {
        $bolas = [
            $row['b1'], $row['b2'], $row['b3'], $row['b4'], $row['b5'],
            $row['b6'], $row['b7'], $row['b8'], $row['b9'], $row['b10'],
            $row['b11'], $row['b12'], $row['b13'], $row['b14'], $row['b15']
        ];
        
        // Frequência
        foreach ($bolas as $b) {
            $frequencia_dezenas[(int)$b]++;
            $dezenas_achadas_atraso[(int)$b] = true;
        }

        // Atraso (Se a dezena ainda não apareceu nos concursos mais recentes)
        for ($i = 1; $i <= 25; $i++) {
            if (!$dezenas_achadas_atraso[$i]) {
                $atraso_dezenas[$i]++;
            }
        }

        $somas[] = (int)$row['soma_dezenas'];
        $concursos_labels[] = (int)$row['concurso'];
        
        $padrao_pi = $row['qtd_pares'] . 'P/' . $row['qtd_impares'] . 'I';
        if (!isset($pares_impares_padrao[$padrao_pi])) {
            $pares_impares_padrao[$padrao_pi] = 0;
        }
        $pares_impares_padrao[$padrao_pi]++;
    }

    // Ordenar Arrays para os gráficos
    arsort($frequencia_dezenas);
    arsort($atraso_dezenas);
    arsort($pares_impares_padrao);

    // Inverter as arrays para o Chart.js ficar cronológico (da esquerda para direita)
    $somas = array_reverse($somas);
    $concursos_labels = array_reverse($concursos_labels);

    // Último concurso para o Top Card
    $ultimo = $resultados[0];

    echo json_encode([
        'status' => 'success',
        'limit' => $limit,
        'ultimo_concurso' => [
            'concurso' => $ultimo['concurso'],
            'data' => $ultimo['data_sorteio'],
            'dezenas' => [
                $ultimo['b1'], $ultimo['b2'], $ultimo['b3'], $ultimo['b4'], $ultimo['b5'],
                $ultimo['b6'], $ultimo['b7'], $ultimo['b8'], $ultimo['b9'], $ultimo['b10'],
                $ultimo['b11'], $ultimo['b12'], $ultimo['b13'], $ultimo['b14'], $ultimo['b15']
            ],
            'soma' => $ultimo['soma_dezenas'],
            'pares' => $ultimo['qtd_pares'],
            'impares' => $ultimo['qtd_impares'],
            'primos' => $ultimo['qtd_primos'],
            'repetidas' => $ultimo['repetidas_anterior']
        ],
        'frequencia' => [
            'labels' => array_keys($frequencia_dezenas),
            'data' => array_values($frequencia_dezenas)
        ],
        'atraso' => [
            'labels' => array_keys($atraso_dezenas),
            'data' => array_values($atraso_dezenas)
        ],
        'tendencia_somas' => [
            'labels' => $concursos_labels,
            'data' => $somas
        ],
        'padroes_pares_impares' => [
            'labels' => array_keys($pares_impares_padrao),
            'data' => array_values($pares_impares_padrao)
        ]
    ]);

} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
