<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Menu Principal</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 50px;
        }
        .menu-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 40px 30px;
            text-align: center;
            text-decoration: none;
            color: var(--text-main);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .menu-card:hover {
            transform: translateY(-10px);
            border-color: var(--primary);
            box-shadow: 0 10px 30px var(--primary-glow);
        }
        .menu-icon {
            font-size: 4rem;
            margin-bottom: 20px;
        }
        .menu-title {
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            margin-bottom: 10px;
            color: var(--primary);
        }
        .menu-desc {
            color: var(--text-muted);
            font-size: 1rem;
        }
        .hero {
            text-align: center;
            margin-top: 40px;
        }
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 15px;
            background: linear-gradient(to right, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar" style="justify-content: center;">
        <h1><span>🎱</span> Lotofácil Pro Analytics</h1>
    </nav>

    <div class="container">
        <div class="hero">
            <h1>Selecione o Módulo</h1>
            <p style="color: var(--text-muted); font-size: 1.2rem;">Escolha a ferramenta que deseja utilizar agora.</p>
        </div>

        <div class="menu-grid">
            <a href="dashboard.php" class="menu-card">
                <div class="menu-icon">📊</div>
                <div class="menu-title">Painel Estatístico</div>
                <div class="menu-desc">Análise gráfica de tendências, dezenas mais quentes, atrasadas e reversão à média.</div>
            </a>

            <a href="simulador.php" class="menu-card">
                <div class="menu-icon">🤖</div>
                <div class="menu-title">Simulador e IA</div>
                <div class="menu-desc">Receba palpites otimizados pela IA ou teste seus próprios jogos contra todo o histórico.</div>
            </a>

            <a href="padroes.php" class="menu-card">
                <div class="menu-icon">🔄</div>
                <div class="menu-title">Padrões e Ciclos</div>
                <div class="menu-desc">Acompanhe o ciclo das dezenas e as estatísticas de Moldura e Miolo.</div>
            </a>

            <a href="fechamento.php" class="menu-card">
                <div class="menu-icon">🎯</div>
                <div class="menu-title">Otimização Matemática</div>
                <div class="menu-desc">Reduza custos usando Teoria dos Conjuntos. Garanta 14 pontos gastando o mínimo possível.</div>
            </a>

            <a href="correlacao.php" class="menu-card">
                <div class="menu-icon">📊</div>
                <div class="menu-title">Matemática Profunda</div>
                <div class="menu-desc">Matriz de Correlação e Alertas de Anomalias Estatísticas (Z-Score).</div>
            </a>

            <a href="importar.php" class="menu-card">
                <div class="menu-icon">📥</div>
                <div class="menu-title">Atualizar Base de Dados</div>
                <div class="menu-desc">Faça o upload do arquivo oficial XLSX da Caixa para processar novos sorteios.</div>
            </a>
        </div>
    </div>

</body>
</html>
