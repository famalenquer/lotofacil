<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Verdades Absolutas</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .record-card {
            background: rgba(255, 0, 0, 0.05);
            border: 1px solid var(--danger);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .record-title {
            color: var(--danger);
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .alert-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
    </style>
</head>
<body>

    <div class="loader-wrapper" id="loader">
        <div style="text-align:center;">
            <div class="loader" style="margin: 0 auto 15px auto;"></div>
            <p id="loader-text" style="color: var(--primary);">Mineirando 3.000 sorteios em busca de recordes...</p>
        </div>
    </div>

    <?php include 'header.php'; ?>

    <div class="container" style="display:none;" id="mainContainer">
        
        <div class="grid-main">
            <!-- Left Column: Atrasos -->
            <div>
                <div class="record-card">
                    <div class="record-title">⚠️ Atrasos Históricos (Limites da Lotofácil)</div>
                    <p class="stat-desc" style="margin-bottom: 20px;">
                        Saiba qual foi o <strong>máximo de tempo</strong> que uma dezena já ficou sem sair em toda a história, e compare com o atraso de hoje.
                    </p>
                    
                    <div id="atrasosList">
                        <!-- Gerado via JS -->
                    </div>
                </div>
            </div>
            
            <!-- Right Column: Top 5 e Sequências -->
            <div>
                <div class="card" style="margin-bottom: 20px;">
                    <div class="card-title">🏆 Top 5 de Todos os Tempos</div>
                    <p class="stat-desc" style="margin-bottom: 15px;">As pedras que mais saíram na história do jogo.</p>
                    <div id="top5List" style="display:flex; flex-direction:column; gap:10px;"></div>
                </div>
                
                <div class="card" style="border: 1px solid var(--primary);">
                    <div class="card-title">🚂 A Maior "Escadinha" da História</div>
                    <p class="stat-desc" style="margin-bottom: 15px;">O recorde absoluto de dezenas sequenciais sorteadas de uma só vez (ex: 1, 2, 3, 4...).</p>
                    
                    <div style="text-align:center;">
                        <div class="stat-value" id="maiorSeqNum">--</div>
                        <div style="color: var(--text-muted); margin-bottom: 15px;">Dezenas Seguidas (Concurso <span id="concursoSeq">--</span>)</div>
                        <div class="dezenas-container" id="seqBolas" style="justify-content:center;"></div>
                    </div>
                </div>
            </div>
        </div>
        
    </div>

    <script src="assets/js/records.js?v=<?php echo time(); ?>"></script>
</body>
</html>
