<?php
$payload = json_encode([
    'concurso_alvo' => 3120,
    'sorteadas' => [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    'dezenas_base' => [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],
    'dezenas_fixas' => [1,2,3],
    'lucro' => 10.0
]);

$pythonScript = dirname(__DIR__) . '/python_scripts/diagnostico_ia.py';
$tempFile = sys_get_temp_dir() . '/payload_' . uniqid() . '.json';
file_put_contents($tempFile, $payload);
$cmd = "python \"$pythonScript\" \"$tempFile\"";
$laudoJson = shell_exec($cmd);
@unlink($tempFile);

echo "Command: " . $cmd . "\n";
echo "Raw Output:\n" . $laudoJson . "\n";
