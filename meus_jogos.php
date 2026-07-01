<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Meus Jogos</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .jogo-card {
            background: rgba(255,255,255,0.03); 
            border: 1px solid var(--card-border);
            border-radius: 8px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        .jogo-header {
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 15px; margin-bottom: 15px;
        }
        .dezena-bola {
            display: inline-block; width: 30px; height: 30px; line-height: 28px;
            text-align: center; border-radius: 50%; background: rgba(255,255,255,0.05);
            border: 1px solid var(--secondary); color: var(--text-main);
            margin: 2px; font-weight: bold; font-size: 0.9rem;
        }
        .dezena-bola.fixa {
            background: linear-gradient(135deg, #fbbf24, #b45309);
            border-color: #fef08a; color: #fff;
        }
        .dezena-bola.hit {
            background: #10b981; border-color: #059669; color: #fff;
        }
        .dezena-bola.miss {
            background: #ef4444; border-color: #b91c1c; color: #fff;
        }
        .dezena-bola.fixa.hit {
            background: linear-gradient(135deg, #10b981, #059669); /* Gradiente Verde */
            border-color: #34d399; color: #fff;
        }
        .analise-box {
            background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;
            margin-top: 15px; display: none; border-left: 4px solid var(--primary);
        }
        .prize-row {
            display: flex; justify-content: space-between; padding: 8px 0;
            border-bottom: 1px dashed rgba(255,255,255,0.1);
        }
        .lucro-positivo { color: #10b981; font-weight: bold; }
        .lucro-negativo { color: #ef4444; font-weight: bold; }
    </style>
</head>
<body>

    <div class="loader-wrapper" id="loader" style="display:none; opacity:0;">
        <div class="loader"></div>
    </div>

    <?php include 'header.php'; ?>

    <div class="container">
        <?php
        try {
            $pdo = new PDO('mysql:host=localhost;dbname=lotofacil_db;charset=utf8mb4', 'root', '');
            $stmt = $pdo->query("SELECT * FROM jogos_salvos ORDER BY id DESC");
            $jogos = $stmt->fetchAll(PDO::FETCH_ASSOC);

            if (empty($jogos)) {
                echo "<div class='card' style='text-align: center; padding: 40px;'><h3 style='color: var(--text-muted);'>Nenhum jogo salvo ainda. Vá até a aba Matriz para gerar e salvar.</h3></div>";
            } else {
                foreach ($jogos as $jogo) {
                    $fixas = json_decode($jogo['dezenas_fixas'], true) ?: [];
                    $base = json_decode($jogo['dezenas_base'], true) ?: [];
                    
                    sort($fixas);
                    sort($base);
                    
                    echo "<div class='jogo-card' id='jogo-{$jogo['id']}'>";
                    
                    echo "<div class='jogo-header'>";
                    echo "<div><h3 style='color: var(--primary); margin: 0; display: flex; align-items: center; gap: 10px;'>{$jogo['nome_estrategia']} <button onclick='excluirJogo({$jogo['id']})' style='background: none; border: none; cursor: pointer; font-size: 1.1rem; filter: grayscale(100%); transition: 0.3s;' onmouseover='this.style.filter=\"none\"' onmouseout='this.style.filter=\"grayscale(100%)\"' title='Excluir Jogo'>🗑️</button></h3>";
                    echo "<small style='color: var(--text-muted);'>Salvo em: " . date('d/m/Y H:i', strtotime($jogo['criado_em'])) . "</small></div>";
                    echo "<div style='text-align: right;'><strong>{$jogo['qtd_jogos']} Jogos</strong><br>Custo: R$ " . number_format($jogo['custo'], 2, ',', '.') . "</div>";
                    echo "</div>";
                    
                    echo "<div id='fixas-{$jogo['id']}' style='margin-bottom: 10px;'><strong>Dezenas Fixas:</strong> ";
                    if (empty($fixas)) {
                        echo "Nenhuma";
                    } else {
                        foreach ($fixas as $f) {
                            echo "<span class='dezena-bola fixa' data-num='$f'>" . str_pad($f, 2, '0', STR_PAD_LEFT) . "</span>";
                        }
                    }
                    echo "</div>";
                    
                    echo "<div id='base-{$jogo['id']}'><strong>Universo de Dezenas Base (" . count($base) . "):</strong><br>";
                    foreach ($base as $b) {
                        $isFixa = in_array($b, $fixas) ? 'fixa' : '';
                        echo "<span class='dezena-bola $isFixa' data-num='$b'>" . str_pad($b, 2, '0', STR_PAD_LEFT) . "</span>";
                    }
                    echo "</div>";
                    
                    $volantes = json_decode($jogo['jogos'], true) ?: [];
                    echo "<div style='margin-top: 15px;'>";
                    echo "<details style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); border-radius: 5px; padding: 10px;'>";
                    echo "<summary style='cursor: pointer; font-weight: bold; color: var(--text-main); outline: none;'>Ver Volantes Gerados (" . count($volantes) . ")</summary>";
                    echo "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; margin-top: 10px;'>";
                    foreach ($volantes as $idx => $volante) {
                        echo "<div style='background: rgba(0,0,0,0.2); padding: 10px; border-radius: 5px; border: 1px solid var(--card-border);'>";
                        echo "<div style='font-size: 0.8rem; color: var(--text-muted); margin-bottom: 5px;'>Jogo " . ($idx + 1) . "</div>";
                        foreach ($volante as $n) {
                            $isFixa = in_array($n, $fixas) ? 'fixa' : '';
                            echo "<span class='dezena-bola $isFixa' style='width: 24px; height: 24px; line-height: 22px; font-size: 0.8rem; margin: 1px;'>" . str_pad($n, 2, '0', STR_PAD_LEFT) . "</span>";
                        }
                        echo "</div>";
                    }
                    echo "</div>";
                    echo "</details>";
                    echo "</div>";
                    
                    echo "<div style='margin-top: 15px;'>";
                    if (!empty($jogo['concurso_alvo'])) {
                        echo "<button class='btn' onclick='analisarJogo({$jogo['id']}, true)' style='background: #10b981; padding: 8px 15px; border-radius: 5px;'>✅ Ver Resultado Salvo (Conc. {$jogo['concurso_alvo']})</button>";
                    } else {
                        echo "<button class='btn' onclick='analisarJogo({$jogo['id']}, false)' style='background: var(--primary); padding: 8px 15px; border-radius: 5px;'>📊 Conferir Resultado (Último Sorteio)</button>";
                    }
                    echo "</div>";
                    
                    echo "<div class='analise-box' id='analise-{$jogo['id']}'></div>";
                    
                    echo "</div>";
                }
            }
        } catch (Exception $e) {
            echo "<div class='alert alert-error'>Erro ao carregar banco de dados: " . $e->getMessage() . "</div>";
        }
        ?>
    </div>

    <script src="assets/js/meus_jogos.js?v=<?php echo time(); ?>"></script>
</body>
</html>
