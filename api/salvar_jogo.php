<?php
header('Content-Type: application/json');

// Habilita exibição de erros para debug interno
ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Recebe o JSON
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);
    
    if (!$data) {
        throw new Exception("Dados inválidos ou vazios.");
    }
    
    $nome_estrategia = $data['nome_estrategia'] ?? 'Fechamento';
    $dezenas_base = json_encode($data['dezenas_base'] ?? []);
    $dezenas_fixas = json_encode($data['dezenas_fixas'] ?? []);
    $jogos = json_encode($data['jogos'] ?? []);
    $qtd_jogos = (int)($data['qtd_jogos'] ?? 0);
    $custo = (float)($data['custo'] ?? 0);
    
    $stmt = $pdo->prepare("
        INSERT INTO jogos_salvos 
        (nome_estrategia, dezenas_base, dezenas_fixas, jogos, qtd_jogos, custo)
        VALUES (?, ?, ?, ?, ?, ?)
    ");
    
    $stmt->execute([
        $nome_estrategia,
        $dezenas_base,
        $dezenas_fixas,
        $jogos,
        $qtd_jogos,
        $custo
    ]);
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Jogo salvo com sucesso!',
        'id' => $pdo->lastInsertId()
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
