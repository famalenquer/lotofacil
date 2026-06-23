<?php
// config/db.php

$host = 'localhost'; // Host do banco de dados
$dbname = 'lotofacil_db'; // Nome do banco de dados
$username = 'root'; // Usuário do MySQL (ajuste conforme seu ambiente WAMP)
$password = ''; // Senha do MySQL (vazia por padrão no WAMP)

try {
    // Configuração do DSN (Data Source Name)
    $dsn = "mysql:host=$host;dbname=$dbname;charset=utf8mb4";
    
    // Opções do PDO
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION, // Lança exceções em caso de erro
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,       // Retorna arrays associativos por padrão
        PDO::ATTR_EMULATE_PREPARES   => false,                  // Desativa emulação para maior segurança
    ];

    // Criando a instância do PDO
    $pdo = new PDO($dsn, $username, $password, $options);
    
} catch (PDOException $e) {
    // Tratamento de erro de conexão
    die("Erro na conexão com o banco de dados: " . $e->getMessage());
}
