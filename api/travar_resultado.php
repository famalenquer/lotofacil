<?php
header('Content-Type: application/json');

ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);
    
    if (!$data || !isset($data['id']) || !isset($data['concurso_alvo'])) {
        throw new Exception("Dados inválidos ou vazios.");
    }
    
    $id = (int)$data['id'];
    $concurso_alvo = (int)$data['concurso_alvo'];
    
    $stmt = $pdo->prepare("UPDATE jogos_salvos SET concurso_alvo = ? WHERE id = ?");
    $stmt->execute([$concurso_alvo, $id]);
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Resultado travado com sucesso!'
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
