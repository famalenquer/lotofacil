<?php
header('Content-Type: application/json');

$host = 'localhost';
$db   = 'lotofacil_db';
$user = 'root';
$pass = '';
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    echo json_encode(["status" => "error", "message" => "Database connection failed"]);
    exit;
}

$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 100;

try {
    // Pegar os ultimos concursos
    $stmt = $pdo->prepare("SELECT * FROM estatisticas_concurso_ext ORDER BY concurso DESC LIMIT :limit");
    $stmt->bindParam(':limit', $limit, PDO::PARAM_INT);
    $stmt->execute();
    $stats = $stmt->fetchAll();

    if (empty($stats)) {
        echo json_encode(["status" => "error", "message" => "Nenhum dado estatístico encontrado."]);
        exit;
    }

    $count = count($stats);

    $sums = [
        'faixa_baixa' => 0, 'faixa_media' => 0, 'faixa_alta' => 0,
        'linha_1' => 0, 'linha_2' => 0, 'linha_3' => 0, 'linha_4' => 0, 'linha_5' => 0,
        'coluna_1' => 0, 'coluna_2' => 0, 'coluna_3' => 0, 'coluna_4' => 0, 'coluna_5' => 0,
        'seq_2' => 0, 'seq_3' => 0,
        'gap_1' => 0, 'gap_2_3' => 0, 'gap_4_plus' => 0,
        'repet_n1' => 0, 'repet_n2' => 0, 'repet_n3' => 0,
        'soma_pares' => 0, 'soma_impares' => 0, 'soma_primos' => 0
    ];

    foreach ($stats as $row) {
        foreach ($sums as $key => $val) {
            $sums[$key] += $row[$key];
        }
    }

    $averages = [];
    foreach ($sums as $key => $val) {
        $averages[$key] = round($val / $count, 2);
    }

    echo json_encode([
        "status" => "success",
        "limit" => $count,
        "medias" => $averages
    ]);

} catch (Exception $e) {
    echo json_encode(["status" => "error", "message" => $e->getMessage()]);
}
?>
