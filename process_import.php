<?php
// process_import.php
require_once 'config/db.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !isset($_FILES['arquivo'])) {
    header('Location: importar.php?status=error&msg=Acesso inválido.');
    exit;
}

$arquivo = $_FILES['arquivo'];

if ($arquivo['error'] !== UPLOAD_ERR_OK) {
    header('Location: importar.php?status=error&msg=Erro no upload do arquivo.');
    exit;
}

// Verifica se é XLSX
$ext = pathinfo($arquivo['name'], PATHINFO_EXTENSION);
if (strtolower($ext) !== 'xlsx') {
    header('Location: importar.php?status=error&msg=Por favor, envie um arquivo .xlsx válido.');
    exit;
}

// Salva o arquivo temporariamente
$uploadDir = __DIR__ . '/uploads/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}

$tempFile = $uploadDir . 'temp_' . time() . '.xlsx';

if (!move_uploaded_file($arquivo['tmp_name'], $tempFile)) {
    header('Location: importar.php?status=error&msg=Erro ao salvar o arquivo temporário.');
    exit;
}

// Caminho absoluto do Python para evitar problemas de PATH no WAMP
$pythonExe = 'C:\\Users\\Fabiano\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe';

// Chama o script Python
$pythonScript = __DIR__ . '/python_scripts/import_xlsx.py';
// Montar o comando escapando apenas os argumentos e mantendo o redirecionamento de erro
$cmd = escapeshellarg($pythonExe) . ' ' . escapeshellarg($pythonScript) . ' ' . escapeshellarg($tempFile) . ' 2>&1';

// Executa o comando
$output = shell_exec($cmd);

// Remove o arquivo temporário após o processamento
@unlink($tempFile);

if (!$output) {
    header('Location: index.php?status=error&msg=' . urlencode('O script Python falhou e não retornou saída alguma. Comando: ' . $cmd));
    exit;
}

$resultado = json_decode(trim($output), true);

if (json_last_error() === JSON_ERROR_NONE && isset($resultado['status'])) {
    if ($resultado['status'] === 'success') {
        header('Location: index.php?status=success&inserted=' . $resultado['inserted']);
    } else {
        header('Location: index.php?status=error&msg=' . urlencode($resultado['message']));
    }
} else {
    header('Location: index.php?status=error&msg=' . urlencode('Erro desconhecido no processamento: ' . $output));
}
exit;
