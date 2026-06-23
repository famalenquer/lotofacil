<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - IA e Simulador</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .volante { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; max-width: 300px; margin: 20px auto; }
        .bola-btn { 
            width: 45px; height: 45px; border-radius: 50%; border: 2px solid var(--card-border); 
            background: var(--bg-color); color: var(--text-main); font-weight: bold; font-size: 1.1rem;
            cursor: pointer; transition: 0.2s; 
        }
        .bola-btn.selected {
            background: linear-gradient(135deg, #a855f7, #7e22ce); border-color: #a855f7; color: white;
            box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
        }
        .btn {
            background: var(--primary); color: var(--bg-color); border: none; padding: 12px 24px;
            font-size: 1rem; font-weight: bold; border-radius: 8px; cursor: pointer; transition: 0.3s;
            display: inline-flex; align-items: center; gap: 8px;
        }
        .btn:hover { box-shadow: 0 0 15px var(--primary-glow); transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }
        
        .result-box { margin-top: 20px; padding: 15px; border-radius: 8px; background: rgba(0,0,0,0.2); }
        
        .prize-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--card-border); }
        .prize-row:last-child { border-bottom: none; }
        
        .sugestao-card {
            background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 15px;
            border-left: 4px solid var(--primary);
        }
    </style>
</head>
<body>

    <!-- Loader -->
    <div class="loader-wrapper" id="loader" style="display:none; opacity:0;">
        <div style="text-align:center;">
            <div class="loader" style="margin: 0 auto 15px auto;"></div>
            <p id="loader-text" style="color: var(--primary);">Processando IA...</p>
        </div>
    </div>

    <!-- Navbar -->
    <nav class="navbar">
        <h1><span>🤖</span> Lotofácil Pro - IA & Simulador</h1>
        <div class="controls">
            <button onclick="window.location.href='index.php'" class="btn" style="background: var(--secondary); color: white;">Voltar ao Menu</button>
        </div>
    </nav>

    <div class="container">
        <div class="grid-main">
            <!-- Left: Motor Preditivo -->
            <div class="card">
                <div class="card-title">🧠 Motor de Sugestões Preditivas (IA)</div>
                <p class="stat-desc" style="margin-bottom: 20px;">
                    O sistema utiliza Média Móvel Ponderada cruzando o histórico geral (20%), últimos 100 jogos (30%) e últimos 20 jogos (50%). 
                    Apenas jogos com filtro matemático perfeito são exibidos.
                </p>
                
            <!-- Configurações de Geração -->
            <div class="card" style="margin-top: 20px;">
                <div class="card-title">⚙️ Configurações do Meta-Simulador</div>
                <div style="display: flex; gap: 15px; margin-top: 15px;">
                    <div style="flex: 1;">
                        <label style="color:var(--text-muted); font-size:0.9rem;">Dezenas por Volante (15 a 20)</label>
                        <input type="number" id="tamanhoJogo" value="15" min="15" max="20" style="width:100%; padding:8px; border-radius:5px; border:1px solid var(--primary); background:var(--bg-color); color:white; margin-top:5px;">
                    </div>
                    <div style="flex: 1;">
                        <label style="color:var(--text-muted); font-size:0.9rem;">Quantos Jogos Gerar?</label>
                        <input type="number" id="qtdJogos" value="3" min="1" max="50" style="width:100%; padding:8px; border-radius:5px; border:1px solid var(--primary); background:var(--bg-color); color:white; margin-top:5px;">
                    </div>
                </div>
            </div>

            <!-- Sugestões da IA -->
            <div class="card" style="margin-top: 20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
                    <div class="card-title" style="margin:0;">🧠 Motor Preditivo (IA)</div>
                    <button class="btn" onclick="gerarSugestoes()" style="width:auto; font-size:0.9rem; padding: 8px 15px;">⚡ Gerar Inteligente</button>
                </div>
                
                <p class="stat-desc">
                    O Algoritmo Híbrido (Machine Learning + Estatística) formará volantes otimizados. <strong>O sistema fará o Backtesting massivo de todos eles no histórico automaticamente!</strong>
                </p>
                
                <div id="ia-results" style="margin-top: 30px;">
                    <!-- Palpites virão aqui -->
                </div>
            </div>
            </div>

            <!-- Right: Simulador / Backtesting -->
            <div class="card">
                <div class="card-title">⏱️ Backtesting (Testar Jogo)</div>
                <p class="stat-desc" style="margin-bottom: 10px;">
                    Selecione de 15 a 20 dezenas e descubra quantas vezes esse jogo já teria ganhado na história da Lotofácil.
                </p>
                
                <div style="text-align: center;">
                    <span id="contador-bolas" style="font-weight:bold; color: var(--primary);">0</span> / 20 selecionadas
                </div>
                
                <div class="volante" id="volante">
                    <!-- Gerado via JS -->
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn" style="background: var(--secondary); color:white;" onclick="testarJogo()" id="btnTestar">🎯 Testar contra o Histórico</button>
                    <button class="btn" style="background: transparent; border: 1px solid var(--text-muted); margin-left:10px;" onclick="limparVolante()">Limpar</button>
                </div>
                
                <div id="test-results" class="result-box" style="display:none;">
                    <h3 style="margin-bottom: 15px; color: var(--primary);">Resultados Históricos</h3>
                    <div id="prize-list"></div>
                </div>
            </div>
        </div>
    </div>

    <script src="assets/js/simulador.js"></script>
</body>
</html>
