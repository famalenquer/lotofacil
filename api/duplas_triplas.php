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
    PDO::ATTR_EMULATE_PREPARES   => true,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    echo json_encode(["status" => "error", "message" => "Database connection failed"]);
    exit;
}

$janela = isset($_GET['janela']) ? $_GET['janela'] : 'all';
$tipo = isset($_GET['tipo']) ? $_GET['tipo'] : 'dupla';

if ($tipo === 'dupla') {
    $dez_base = isset($_GET['dezena']) ? (int)$_GET['dezena'] : 0;
    if ($dez_base < 1 || $dez_base > 25) {
        echo json_encode(["status" => "error", "message" => "Dezena inválida"]);
        exit;
    }

    // Busca duplas fortes (onde uma das dezenas é a dezena base)
    $stmt = $pdo->prepare("
        SELECT 
            IF(dez_1 = :dez, dez_2, dez_1) as parceira,
            ocorrencias_juntas,
            IF(dez_1 = :dez, prob_condicional_2_dado_1, prob_condicional_1_dado_2) as prob_condicional,
            afinidade
        FROM estatisticas_duplas 
        WHERE janela = :janela AND (dez_1 = :dez OR dez_2 = :dez)
        ORDER BY prob_condicional DESC, afinidade DESC
        LIMIT 10
    ");
    $stmt->execute(['dez' => $dez_base, 'janela' => $janela]);
    $resultados = $stmt->fetchAll();

    echo json_encode([
        "status" => "success",
        "tipo" => "dupla",
        "dezena_base" => $dez_base,
        "parceiras" => $resultados
    ]);

} else if ($tipo === 'tripla') {
    $dez1 = isset($_GET['dez1']) ? (int)$_GET['dez1'] : 0;
    $dez2 = isset($_GET['dez2']) ? (int)$_GET['dez2'] : 0;
    
    if ($dez1 < 1 || $dez1 > 25 || $dez2 < 1 || $dez2 > 25 || $dez1 == $dez2) {
        echo json_encode(["status" => "error", "message" => "Dezenas base inválidas"]);
        exit;
    }

    // O script python insere as 3 permutações (i,j,k), (i,k,j) e (j,k,i) para que os dois primeiros sejam a base
    // Vamos garantir a ordem para bater com o banco, ou só usar (dez_1 = :d1 AND dez_2 = :d2) OR (dez_1 = :d2 AND dez_2 = :d1)
    
    $stmt = $pdo->prepare("
        SELECT 
            dez_3 as completa,
            ocorrencias_juntas,
            prob_condicional_k_dado_ij as prob_condicional
        FROM estatisticas_triplas 
        WHERE janela = :janela 
          AND ((dez_1 = :d1 AND dez_2 = :d2) OR (dez_1 = :d2 AND dez_2 = :d1))
        ORDER BY prob_condicional_k_dado_ij DESC
        LIMIT 10
    ");
    $stmt->execute(['d1' => $dez1, 'd2' => $dez2, 'janela' => $janela]);
    $resultados = $stmt->fetchAll();

    echo json_encode([
        "status" => "success",
        "tipo" => "tripla",
        "dupla_base" => [$dez1, $dez2],
        "completam" => $resultados
    ]);
} else {
    echo json_encode(["status" => "error", "message" => "Tipo inválido"]);
}
?>
