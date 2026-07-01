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
                <option value="10">Últimos 10 Sorteios</option>
                <option value="20" selected>Últimos 20 Sorteios</option>
                <option value="30">Últimos 30 Sorteios</option>
                <option value="50">Últimos 50 Sorteios</option>
                <option value="100">Últimos 100 Sorteios</option>
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

        <!-- Últimos Jogos (Cartelas) -->
        <div class="card" style="margin-bottom: 30px; background: rgba(30, 20, 45, 0.8);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="card-title" style="margin: 0; font-size: 1.2rem; color: #fff;">🎟️ Últimos Sorteios em Cartelas</div>
                    <div class="stat-desc" style="margin-top: 5px;">Visualize os resultados reais no formato do volante</div>
                </div>
                <select id="cartelasFilter" style="padding: 8px 15px; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; border: 1px solid var(--card-border); font-size: 0.95rem; cursor: pointer; transition: 0.3s;">
                    <option value="5">Últimos 5 jogos</option>
                    <option value="10" selected>Últimos 10 jogos</option>
                    <option value="15">Últimos 15 jogos</option>
                    <option value="20">Últimos 20 jogos</option>
                </select>
            </div>
            
            <div id="cartelasContainer" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding-bottom: 15px; padding-top: 10px;">
                <!-- Cartelas serão injetadas via JS -->
            </div>
        </div>

        <!-- Estatísticas Avançadas (Nova Seção) -->
        <div class="card" style="margin-bottom: 30px; background: rgba(30, 20, 45, 0.8);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="card-title" style="margin: 0; font-size: 1.2rem; color: #fff;">🧩 Estatísticas Avançadas (Distribuição, Linhas e Somas)</div>
                    <div class="stat-desc" style="margin-top: 5px;">Médias do período selecionado</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <!-- Distribuição B/M/A -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px;">Distribuição Média (B / M / A)</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #fff;" id="statDistBMA">-- / -- / --</div>
                    <div style="font-size: 0.75rem; color: #a0aec0; margin-top: 5px;">Baixas (01-08) / Médias (09-17) / Altas (18-25)</div>
                </div>

                <!-- Somas Específicas -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px;">Médias de Somas</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #fff;" id="statSomas">P: -- | Í: -- | Pr: --</div>
                    <div style="font-size: 0.75rem; color: #a0aec0; margin-top: 5px;">Soma de Pares / Ímpares / Primos</div>
                </div>

                <!-- Sequências e Gaps -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px;">Sequências Média</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #fff;" id="statSeqs">Duplas: -- | Triplas: --</div>
                    <div style="font-size: 0.75rem; color: #a0aec0; margin-top: 5px;">Gaps > 3: <span id="statGap4">--</span> por concurso</div>
                </div>
                
                <!-- Repetições -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px;">Repetições Múltiplas</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: #fff;" id="statRepeticoes">n-1: -- | n-2: --</div>
                    <div style="font-size: 0.75rem; color: #a0aec0; margin-top: 5px;">Repetidas dos concursos anteriores</div>
                </div>
            </div>
            
            <div style="margin-top: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <!-- Mini Gráficos (Linhas e Colunas) -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px; text-align: center;">Média de Dezenas por Linha</div>
                    <div style="height: 120px;">
                        <canvas id="chartLinhas"></canvas>
                    </div>
                </div>
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px; text-align: center;">Média de Dezenas por Coluna</div>
                    <div style="height: 120px;">
                        <canvas id="chartColunas"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Conexões Fortes (Duplas e Triplas) -->
        <div class="card" style="margin-bottom: 30px; background: rgba(20, 30, 45, 0.8);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="card-title" style="margin: 0; font-size: 1.2rem; color: #fff;">🔗 Conexões Fortes (Co-ocorrência Estatística)</div>
                    <div class="stat-desc" style="margin-top: 5px;">Quais dezenas costumam sair juntas?</div>
                </div>
                <select id="coocorrenciaFilter" style="padding: 8px 15px; border-radius: 8px; background: rgba(255,255,255,0.05); color: white; border: 1px solid var(--card-border); font-size: 0.95rem; cursor: pointer; transition: 0.3s;">
                    <option value="10">Últimos 10 jogos</option>
                    <option value="20">Últimos 20 jogos</option>
                    <option value="50">Últimos 50 jogos</option>
                    <option value="100">Últimos 100 jogos</option>
                    <option value="all" selected>Todo o Histórico</option>
                </select>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <!-- Duplas Fortes -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <div style="color: var(--text-muted); font-size: 1rem; font-weight: bold;">Duplas Fortes</div>
                        <select id="dezenaBaseSelect" style="padding: 5px 10px; border-radius: 6px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2);">
                            <!-- Injected via JS -->
                        </select>
                    </div>
                    <table style="width: 100%; text-align: center; border-collapse: collapse; font-size: 0.9rem;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: #a0aec0;">
                                <th style="padding: 8px;">Parceira</th>
                                <th style="padding: 8px;">Prob. Condicional</th>
                                <th style="padding: 8px;">Ocorrências</th>
                                <th style="padding: 8px;">Afinidade</th>
                            </tr>
                        </thead>
                        <tbody id="duplasTabela">
                            <!-- Injected via JS -->
                        </tbody>
                    </table>
                </div>

                <!-- Triplas Fortes -->
                <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <div style="color: var(--text-muted); font-size: 1rem; font-weight: bold;">Triplas Fortes</div>
                        <div style="display: flex; gap: 5px;">
                            <select id="triplaBase1Select" style="padding: 5px 10px; border-radius: 6px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2);"></select>
                            <span style="color: white; line-height: 28px;">&amp;</span>
                            <select id="triplaBase2Select" style="padding: 5px 10px; border-radius: 6px; background: rgba(255,255,255,0.1); color: white; border: 1px solid rgba(255,255,255,0.2);"></select>
                        </div>
                    </div>
                    <table style="width: 100%; text-align: center; border-collapse: collapse; font-size: 0.9rem;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: #a0aec0;">
                                <th style="padding: 8px;">Completa</th>
                                <th style="padding: 8px;">Prob. Condicional</th>
                                <th style="padding: 8px;">Ocorrências</th>
                            </tr>
                        </thead>
                        <tbody id="triplasTabela">
                            <!-- Injected via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Main Heatmap & AI Area -->
        <div class="grid-main">
            <!-- Left Column: Heatmap and Table -->
            <div class="main-column">
                <div class="card" style="margin-bottom: 30px; text-align: center;">
                    <div class="card-title" style="font-size: 1.2rem;">🔥 Mapa de Calor do Período (Cartela)</div>
                    <div class="stat-desc" style="margin-bottom: 20px;">Frequência das dezenas no recorte selecionado</div>
                    
                    <div id="heatmapVolante" style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; max-width: 350px; margin: 0 auto; margin-bottom: 25px;">
                        <!-- Volante injetado via JS -->
                    </div>
                    
                    <div style="max-width: 350px; margin: 0 auto;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 5px;">
                            <span>❄️ Fria (Saiu Pouco)</span>
                            <span>🔥 Quente (Saiu Muito)</span>
                        </div>
                        <div style="height: 10px; width: 100%; border-radius: 5px; background: linear-gradient(to right, hsl(220, 80%, 40%), hsl(110, 80%, 40%), hsl(0, 80%, 40%)); border: 1px solid rgba(255,255,255,0.1);"></div>
                    </div>
                </div>

                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">📊 Raio-X Completo (Motor AI)</div>
                    <table style="width: 100%; border-collapse: collapse; text-align: center; margin-top: 15px;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <th style="padding: 10px;">Dezena</th>
                                <th style="padding: 10px;">Probabilidade (IA)</th>
                                <th style="padding: 10px;">Atraso</th>
                                <th style="padding: 10px;">Status</th>
                            </tr>
                        </thead>
                        <tbody id="raioxTabela">
                            <!-- Tabela injetada via JS -->
                        </tbody>
                    </table>
                </div>

                <div class="card" style="margin-bottom: 30px;">
                    <div class="card-title">Frequência das Dezenas (Histórico)</div>
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

            <!-- Right Column: Lists and secondary charts -->
            <div class="side-column">
                <div class="card" style="margin-bottom: 30px; border-left: 4px solid #ef4444;">
                    <div class="card-title">🔥 Dezenas Quentes</div>
                    <div class="stat-desc" style="margin-bottom: 10px;">Maior probabilidade pela IA</div>
                    <ul class="ranking-list" id="quentesList">
                        <!-- Injected via JS -->
                    </ul>
                </div>

                <div class="card" style="margin-bottom: 30px; border-left: 4px solid #3b82f6;">
                    <div class="card-title">❄️ Dezenas Frias (Atrasadas)</div>
                    <div class="stat-desc" style="margin-bottom: 10px;">Há mais tempo sem sair</div>
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

    <script src="assets/js/dashboard.js?v=<?php echo time(); ?>"></script>
    <script src="assets/js/dashboard_stats.js?v=<?php echo time(); ?>"></script>
    <script src="assets/js/coocorrencia.js?v=<?php echo time(); ?>"></script>
</body>
</html>
