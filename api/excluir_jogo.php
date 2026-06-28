<?php
header('Content-Type: application/json');
ini_set('display_errors', 1);
error_reporting(E_ALL);

try {
    $pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // Suporta GET ou POST
    $id = isset($_REQUEST['id']) ? (int)$_REQUEST['id'] : 0;
    
    if ($id <= 0) {
        throw new Exception("ID inválido.");
    }
    
    $stmt = $pdo->prepare("DELETE FROM jogos_salvos WHERE id = ?");
    $stmt->execute([$id]);
    
    echo json_encode([
        'status' => 'success',
        'message' => 'Jogo excluído com sucesso.'
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>
