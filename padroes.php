<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Padrões Avançados</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .cycle-progress {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        .missing-balls-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
        }
        .missing-ball {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: rgba(250, 204, 21, 0.1);
            border: 2px dashed var(--primary);
            color: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .drawn-ball {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255,255,255,0.05);
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            opacity: 0.5;
        }
    </style>
</head>
<body>

    <!-- Loader -->
    <div class="loader-wrapper" id="loader">
        <div class="loader"></div>
    </div>

    <!-- Navbar -->
    <?php include 'header.php'; ?>

    <div class="container">
        <div class="grid-main">
            <!-- Coluna Esquerda: Ciclo de Dezenas -->
            <div class="main-column">
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">🔄 Análise de Ciclo de Dezenas</div>
                    <p class="stat-desc" style="margin-bottom: 20px;">
                        Um "ciclo" fecha quando todas as 25 dezenas são sorteadas pelo menos uma vez. Use as dezenas faltantes como números fixos nos seus jogos, pois a probabilidade de saírem para fechar o ciclo é muito alta.
                    </p>
                    
                    <div class="cycle-progress">
                        <h3 style="color: var(--text-main); margin-bottom: 5px;">Ciclo Atual: <span id="cicloAtual" style="color: var(--primary);">--</span></h3>
                        <p class="stat-desc">Concursos rodados neste ciclo: <span id="concursosRodados" style="color: white; font-weight: bold;">--</span> (Média histórica para fechar: <span id="mediaCiclo">--</span> concursos)</p>
                    </div>

                    <h4 style="color: var(--primary); margin-bottom: 10px; text-align: center;">🔥 Dezenas Faltantes para Fechar o Ciclo</h4>
                    <div class="missing-balls-container" id="missingBalls">
                        <!-- Bolas Faltantes Injetadas Aqui -->
                    </div>
                    
                    <h4 style="color: var(--text-muted); margin-top: 30px; margin-bottom: 10px; text-align: center;">Dezenas Já Sorteadas neste Ciclo</h4>
                    <div class="missing-balls-container" id="drawnBalls" style="gap: 5px;">
                        <!-- Bolas Sorteadas Injetadas Aqui -->
                    </div>
                </div>
            </div>

            <!-- Coluna Direita: Moldura e Miolo -->
            <div class="side-column">
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">🖼️ Padrão de Moldura e Miolo</div>
                    <p class="stat-desc" style="margin-bottom: 15px;">
                        O volante tem 16 dezenas na Moldura (borda) e 9 no Miolo (centro).
                    </p>
                    
                    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
                        <div class="stat-desc">Média de Moldura (Últimos 100 sorteios)</div>
                        <div class="stat-value" id="mediaMoldura" style="font-size: 2rem;">--</div>
                    </div>
                    
                    <h4 style="color: var(--text-main); margin-bottom: 10px;">Top Padrões Históricos</h4>
                    <ul class="ranking-list" id="molduraList">
                        <!-- Injetado via JS -->
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script src="assets/js/padroes.js"></script>
</body>
</html>
