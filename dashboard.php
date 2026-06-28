<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro Analytics</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

    <!-- Loader -->
    <div class="loader-wrapper" id="loader">
        <div class="loader"></div>
    </div>

    <!-- Navbar -->
    <?php include 'header.php'; ?>

    <div class="container">
        <!-- Dashboard Header & Controls -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
            <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                <h2 style="color: var(--text-main); margin: 0;">Visão Geral do Histórico</h2>
                <a href="https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx" target="_blank" style="padding: 6px 12px; background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; text-decoration: none; font-size: 0.85rem; display: flex; align-items: center; gap: 5px; transition: 0.3s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'">
                    🔗 Resultados da Caixa
                </a>
            </div>
            <select id="periodFilter" style="padding: 8px 15px; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; border: 1px solid var(--card-border); font-size: 1rem; cursor: pointer;">
                <option value="50">Últimos 50 Sorteios</option>
                <option value="100" selected>Últimos 100 Sorteios</option>
                <option value="250">Últimos 250 Sorteios</option>
                <option value="all">Todo o Histórico</option>
            </select>
        </div>

        <!-- Top Cards -->
        <div class="grid-top">
            <div class="card">
                <div class="card-title">Último Sorteio</div>
                <div class="stat-value" id="ultConcurso">----</div>
                <div class="stat-desc" id="ultData">--/--/----</div>
                <div class="dezenas-container" id="ultDezenas">
                    <!-- Dezenas will be injected here -->
                </div>
            </div>

            <div class="card">
                <div class="card-title">Soma das Dezenas</div>
                <div class="stat-value" id="ultSoma">--</div>
                <div class="stat-desc">Ideal: entre 181 e 210</div>
            </div>

            <div class="card">
                <div class="card-title">Pares / Ímpares</div>
                <div class="stat-value" id="ultPI">-- / --</div>
                <div class="stat-desc">Padrão 8/7 ou 7/8 é ideal</div>
            </div>

            <div class="card">
                <div class="card-title">Números Primos</div>
                <div class="stat-value" id="ultPrimos">--</div>
                <div class="stat-desc">Média histórica: 5 a 6</div>
            </div>
            
            <div class="card">
                <div class="card-title">Repetidas (Anterior)</div>
                <div class="stat-value" id="ultRepetidas">--</div>
                <div class="stat-desc">Média histórica: 9</div>
            </div>
        </div>

        <!-- Main Charts Area -->
        <div class="grid-main">
            <!-- Left Column -->
            <div class="main-column">
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">Frequência das Dezenas (Mais Sorteadas)</div>
                    <div class="chart-container">
                        <canvas id="freqChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-title">Tendência da Soma das Dezenas (Reversão à Média)</div>
                    <div class="chart-container">
                        <canvas id="somaChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Right Column -->
            <div class="side-column">
                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">🔥 Dezenas Quentes</div>
                    <ul class="ranking-list" id="quentesList">
                        <!-- Injected via JS -->
                    </ul>
                </div>

                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">❄️ Dezenas Frias (Atrasadas)</div>
                    <div class="stat-desc" style="margin-bottom: 10px;">Concursos sem sair</div>
                    <ul class="ranking-list" id="friasList">
                        <!-- Injected via JS -->
                    </ul>
                </div>

                <div class="card">
                    <div class="card-title">Padrão de Grupos (Pares/Ímpares)</div>
                    <div class="chart-container" style="height: 250px;">
                        <canvas id="piChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="assets/js/dashboard.js"></script>
</body>
</html>
