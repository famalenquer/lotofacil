<?php
// Obtém o nome do arquivo atual para destacar o menu ativo
$currentPage = basename($_SERVER['PHP_SELF']);
?>
<header class="global-header">
    <div class="header-container">
        <div class="header-brand">
            <a href="index.php">
                <span class="logo-icon">🎱</span>
                <span class="brand-text">Lotofácil Pro</span>
            </a>
        </div>
        <nav class="header-nav">
            <a href="dashboard.php" class="<?= $currentPage == 'dashboard.php' ? 'active' : '' ?>"><span class="nav-icon">📊</span><span class="nav-text">Painel</span></a>
            <a href="simulador.php" class="<?= $currentPage == 'simulador.php' ? 'active' : '' ?>"><span class="nav-icon">🤖</span><span class="nav-text">IA</span></a>
            <a href="fechamento.php" class="<?= $currentPage == 'fechamento.php' ? 'active' : '' ?>"><span class="nav-icon">🎯</span><span class="nav-text">Matriz</span></a>
            <a href="meus_jogos.php" class="<?= $currentPage == 'meus_jogos.php' ? 'active' : '' ?>"><span class="nav-icon">💾</span><span class="nav-text">Meus Jogos</span></a>
            <a href="cluster.php" class="<?= $currentPage == 'cluster.php' ? 'active' : '' ?>"><span class="nav-icon">🌦️</span><span class="nav-text">Clima</span></a>
            <a href="records.php" class="<?= $currentPage == 'records.php' ? 'active' : '' ?>"><span class="nav-icon">📜</span><span class="nav-text">Histórico</span></a>
            <a href="padroes.php" class="<?= $currentPage == 'padroes.php' ? 'active' : '' ?>"><span class="nav-icon">🔄</span><span class="nav-text">Ciclos</span></a>
            <a href="correlacao.php" class="<?= $currentPage == 'correlacao.php' ? 'active' : '' ?>"><span class="nav-icon">📈</span><span class="nav-text">Z-Score</span></a>
            <a href="importar.php" class="<?= $currentPage == 'importar.php' ? 'active' : '' ?>"><span class="nav-icon">📥</span><span class="nav-text">Base</span></a>
        </nav>
    </div>
</header>

<?php
$titles = [
    'dashboard.php' => ['icon' => '📊', 'title' => 'Painel Estatístico', 'desc' => 'Visão geral das tendências e análise macro.'],
    'simulador.php' => ['icon' => '🤖', 'title' => 'Simulador e Inteligência Artificial', 'desc' => 'Gere palpites avançados ou faça backtesting de dezenas.'],
    'fechamento.php' => ['icon' => '🎯', 'title' => 'Fechamento Matemático Inteligente', 'desc' => 'Otimização com Teoria dos Conjuntos e Clima.'],
    'meus_jogos.php' => ['icon' => '💾', 'title' => 'Meus Jogos Salvos', 'desc' => 'Gerencie seus bilhetes e confira o desempenho contra o último sorteio.'],
    'cluster.php' => ['icon' => '🌦️', 'title' => 'O Clima da Loteria (K-Means)', 'desc' => 'Mapeamento de Regimes Comportamentais dos Sorteios.'],
    'records.php' => ['icon' => '📜', 'title' => 'Verdades Históricas Absolutas', 'desc' => 'Monitoramento de Atrasos e Limites Matemáticos.'],
    'padroes.php' => ['icon' => '🔄', 'title' => 'Análise de Padrões e Ciclos', 'desc' => 'Comportamento da Moldura, Miolo e Ciclo de Dezenas.'],
    'correlacao.php' => ['icon' => '📈', 'title' => 'Matriz de Correlação & Z-Score', 'desc' => 'Física profunda e anomalias estatísticas.'],
    'importar.php' => ['icon' => '📥', 'title' => 'Atualizar Base de Dados', 'desc' => 'Sincronize o sistema com os últimos resultados da Caixa.']
];

if (isset($titles[$currentPage])) {
    $info = $titles[$currentPage];
    echo "<div style='text-align: center; margin: 30px 0 20px 0;'>";
    echo "<h1 style='font-size: 2.5rem; color: var(--primary); margin-bottom: 5px;'><span>{$info['icon']}</span> {$info['title']}</h1>";
    echo "<p style='color: var(--text-muted); font-size: 1.1rem;'>{$info['desc']}</p>";
    echo "</div>";
}
?>
