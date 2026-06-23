<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Importar Resultados</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .import-container { max-width: 600px; margin: 40px auto; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; margin-bottom: 8px; color: var(--text-main); }
        input[type="file"] { 
            display: block; width: 100%; padding: 15px; 
            background: rgba(255,255,255,0.05); border: 1px dashed var(--secondary); 
            border-radius: 8px; color: var(--text-main); cursor: pointer;
        }
        .btn {
            background: var(--primary); color: var(--bg-color); border: none; padding: 12px 20px; 
            font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; transition: 0.3s;
        }
        .btn:hover { box-shadow: 0 0 15px var(--primary-glow); transform: translateY(-2px); }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 8px; font-weight: bold; }
        .alert-success { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
        .alert-error { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar">
        <h1><span>📥</span> Atualizar Base de Dados</h1>
        <div class="controls">
            <button onclick="window.location.href='index.php'" class="btn" style="background: var(--secondary); color: white; width: auto;">Voltar ao Menu</button>
        </div>
    </nav>

    <div class="container import-container">
        <div class="card">
            <div class="card-title" style="color: var(--primary); font-size: 1.5rem; margin-bottom: 20px;">Importar Resultados da Caixa</div>
            
            <?php
            if (isset($_GET['status'])) {
                if ($_GET['status'] == 'success') {
                    echo '<div class="alert alert-success">Importação concluída com sucesso! ' . intval($_GET['inserted']) . ' novos concursos adicionados.</div>';
                } elseif ($_GET['status'] == 'error') {
                    echo '<div class="alert alert-error">Erro ao importar: ' . htmlspecialchars($_GET['msg']) . '</div>';
                }
            }
            ?>

            <form action="process_import.php" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="arquivo">Selecione o arquivo XLSX da Caixa:</label>
                    <input type="file" name="arquivo" id="arquivo" accept=".xlsx" required>
                    <small style="color: var(--text-muted); display: block; margin-top: 10px;">* Faça o upload da planilha oficial em Excel (.xlsx) baixada do site da Caixa.</small>
                </div>
                <button type="submit" class="btn">Iniciar Importação</button>
            </form>
        </div>
    </div>
</body>
</html>
