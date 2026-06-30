<?php
$pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
$stmt = $pdo->query("SELECT id FROM jogos_salvos LIMIT 1");
$row = $stmt->fetch();
if($row) {
    echo file_get_contents("http://localhost/lotofacil/api/analisar_jogo.php?id=" . $row['id']);
}
