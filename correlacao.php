<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Correlação e Alertas</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .alert-box {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .alert-box.fria {
            background: rgba(59, 130, 246, 0.1);
            border-color: #3b82f6;
            color: #60a5fa;
        }
        .alert-icon { font-size: 1.5rem; }
        
        .corr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .corr-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .corr-badge {
            display: inline-block;
            width: 35px; height: 35px;
            line-height: 33px;
            border-radius: 50%;
            font-weight: bold;
            margin: 2px;
        }
        .bg-good { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #10b981; }
        .bg-bad { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; color: #ef4444; }
        
        .main-dezena {
            font-size: 1.8rem;
            color: var(--primary);
            font-weight: bold;
            margin-bottom: 10px;
            display: inline-block;
            border-bottom: 2px solid var(--primary);
        }
    </style>
</head>
<body>

    <!-- Loader -->
    <div class="loader-wrapper" id="loader">
        <div class="loader"></div>
    </div>

    <!-- Navbar -->
    <nav class="navbar">
        <h1><span>📊</span> Matemática Profunda</h1>
        <div class="controls">
            <button onclick="window.location.href='index.php'" class="btn" style="background: var(--secondary); color: white; width: auto;">Voltar ao Menu</button>
        </div>
    </nav>

    <div class="container">
        <!-- Alertas -->
        <div class="card" style="margin-bottom: 30px;">
            <div class="card-title">🚨 Alertas Estatísticos (Intervalo de Confiança)</div>
            <p class="stat-desc" style="margin-bottom: 20px;">
                Cálculo de Desvio Padrão: Identifica quais dezenas estão sofrendo anomalias matemáticas nos últimos 100 sorteios (Z-Score > 1.96).
            </p>
            <div id="alertasContainer">
                <!-- Injetado via JS -->
            </div>
        </div>

        <!-- Correlação -->
        <div class="card">
            <div class="card-title">🤝 Matriz de Correlação (Top Parceiros)</div>
            <p class="stat-desc" style="margin-bottom: 20px;">
                Mapeamento de Coocorrência. Descubra quais dezenas "andam de mãos dadas" e quais são "inimigas" (nunca saem juntas).
            </p>
            
            <h4 style="color:var(--text-main); margin-bottom:15px;">🔍 Selecione uma dezena para análise:</h4>
            <select id="dezenaSelect" onchange="renderDetalheCorrelacao()" style="font-size: 1.1rem; padding: 10px; margin-bottom: 20px; background: var(--bg-color); color: white; border: 1px solid var(--primary); border-radius: 8px;">
                <!-- Opcoes geradas via JS -->
            </select>
            
            <div id="detalheCorrelacao" class="corr-grid">
                <!-- Injetado via JS -->
            </div>
            
            <h4 style="color:var(--text-main); margin-top:40px; margin-bottom:15px; border-top: 1px solid var(--card-border); padding-top:20px;">🏆 Top 5 Pares Globais (Últimos 100 concursos)</h4>
            <ul class="ranking-list" id="topParesGlobais">
                <!-- Injetado via JS -->
            </ul>
        </div>
    </div>

    <script src="assets/js/correlacao.js"></script>
</body>
</html>
