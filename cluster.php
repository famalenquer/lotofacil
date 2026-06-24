<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Clima da Loteria</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

    <div class="loader-wrapper" id="loader" style="display:none; opacity:0;">
        <div style="text-align:center;">
            <div class="loader" style="margin: 0 auto 15px auto;"></div>
            <p id="loader-text" style="color: var(--primary);">Analisando o clima de 3000 sorteios...</p>
        </div>
    </div>

    <?php include 'header.php'; ?>

    <div class="container">
        <div class="card" style="margin-bottom: 20px; text-align: center;">
            <p class="stat-desc" style="font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
                Este módulo utiliza Machine Learning (<strong>K-Means Não Supervisionado</strong>) para mapear todo o histórico e descobrir os "Regimes Comportamentais" da loteria. Assim você sabe se a tendência atual é de jogos com mais ímpares, somas altas ou muitas dezenas no miolo.
            </p>
            <br>
            <button class="btn" onclick="analisarClima()" style="font-size: 1.2rem; padding: 15px 30px;">🔭 Analisar Cenário Atual</button>
        </div>
        
        <div id="resultados" style="display: none;">
            
            <div class="card" style="margin-bottom: 20px; text-align: center; border: 2px solid var(--primary); box-shadow: 0 0 20px var(--primary-glow);">
                <div class="card-title" style="justify-content: center;">Clima Dominante (Últimos 10 Concursos)</div>
                <div class="stat-value" id="climaAtualId" style="font-size: 3rem;">--</div>
                <p class="stat-desc" id="climaAtualDesc" style="font-size: 1.2rem; margin-top: 10px; color: var(--text-main);"></p>
            </div>

            <h3 style="color: var(--text-main); margin-bottom: 15px;">🌡️ Perfis Históricos Descobertos pela IA:</h3>
            <div class="grid-top" id="clustersGrid">
                <!-- Perfis gerados via JS -->
            </div>
            
        </div>
    </div>

    <script src="assets/js/cluster.js?v=<?php echo time(); ?>"></script>
</body>
</html>
