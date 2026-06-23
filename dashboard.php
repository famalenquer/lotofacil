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
    <nav class="navbar">
        <h1><span>🎱</span> Lotofácil Pro Analytics</h1>
        <div class="controls">
            <select id="periodFilter">
                <option value="20">Últimos 20</option>
                <option value="50">Últimos 50</option>
                <option value="100" selected>Últimos 100</option>
                <option value="500">Últimos 500</option>
            </select>
            <button onclick="window.location.href='index.php'" style="background: var(--card-bg); border: 1px solid var(--card-border); color: white; padding: 8px 15px; border-radius: 8px; cursor: pointer; transition: 0.3s;">Voltar ao Menu</button>
        </div>
    </nav>

    <div class="container">
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
