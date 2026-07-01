<?php
// api/ultimos_jogos.php
header('Content-Type: application/json');
require_once '../config/db.php';

$limitParam = isset($_GET['limit']) ? $_GET['limit'] : '10';
$limit = (int)$limitParam;

if ($limit <= 0) $limit = 10;

try {
    $stmt = $pdo->prepare("
        SELECT * 
        FROM concursos 
        ORDER BY concurso DESC 
        LIMIT :limit
    ");
    $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    
    $resultados = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $jogos = [];
    foreach ($resultados as $row) {
        $jogos[] = [
            'concurso' => $row['concurso'],
            'data' => $row['data_sorteio'],
            'dezenas' => [
                (int)$row['b1'], (int)$row['b2'], (int)$row['b3'], (int)$row['b4'], (int)$row['b5'],
                (int)$row['b6'], (int)$row['b7'], (int)$row['b8'], (int)$row['b9'], (int)$row['b10'],
                (int)$row['b11'], (int)$row['b12'], (int)$row['b13'], (int)$row['b14'], (int)$row['b15']
            ]
        ];
    }

    echo json_encode([
        'status' => 'success',
        'jogos' => $jogos
    ]);

} catch (PDOException $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
