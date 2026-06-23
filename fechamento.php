<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Otimização de Jogos</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .dezena-base {
            display: inline-flex; width: 40px; height: 40px; border-radius: 50%;
            background: linear-gradient(135deg, #facc15, #ca8a04);
            color: #1a1025; font-weight: bold; font-size: 1.1rem;
            align-items: center; justify-content: center; margin: 4px;
            box-shadow: 0 0 10px rgba(250, 204, 21, 0.4);
        }
        
        .volante-grid {
            display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px; margin-top: 20px;
        }
        
        .volante-card {
            background: rgba(255,255,255,0.03); border: 1px solid var(--card-border);
            border-radius: 8px; padding: 15px; position: relative;
        }
        
        .volante-bola {
            display: inline-block; width: 30px; height: 30px; line-height: 28px;
            text-align: center; border-radius: 50%; background: var(--bg-color);
            border: 1px solid var(--secondary); color: var(--text-main);
            margin: 2px; font-weight: bold; font-size: 0.9rem;
        }
        
        .stat-highlight {
            font-size: 2.5rem; color: #10b981; font-weight: bold;
            font-family: 'Outfit', sans-serif;
        }
    </style>
</head>
<body>

    <div class="loader-wrapper" id="loader" style="display:none; opacity:0;">
        <div style="text-align:center;">
            <div class="loader" style="margin: 0 auto 15px auto;"></div>
            <p id="loader-text" style="color: var(--primary);">O algoritmo de Otimização (Set Cover) está calculando a menor matriz matemática possível... (Isso pode levar alguns segundos)</p>
        </div>
    </div>

    <nav class="navbar">
        <h1><span>🎯</span> Fechamento Matemático Inteligente</h1>
        <div class="controls">
            <button onclick="window.location.href='index.php'" class="btn" style="background: var(--secondary); color: white; width: auto;">Voltar ao Menu</button>
        </div>
    </nav>

    <div class="container">
        <div class="card" style="margin-bottom: 20px; text-align: center;">
            <p class="stat-desc" style="font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
                Este algoritmo extrai as <strong>18 dezenas mais poderosas</strong> indicadas pela Inteligência Artificial. Em vez de você jogar as 816 combinações possíveis, a Teoria dos Conjuntos reduz seus bilhetes para garantir <strong>14 Pontos</strong> gastando o mínimo absoluto.
            </p>
            <br>
            <button class="btn" onclick="gerarFechamento()" style="font-size: 1.2rem; padding: 15px 30px;">⚡ Gerar Matriz Reduzida</button>
        </div>
        
        <div id="resultados" style="display: none;">
            <!-- Info do Fechamento -->
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-title" style="text-align: center;">As 18 Dezenas Base Selecionadas pela IA</div>
                <div id="dezenasBase" style="text-align: center; margin: 20px 0;"></div>
                
                <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 30px; border-top: 1px solid var(--card-border); padding-top: 20px;">
                    <div>
                        <div class="stat-desc">Jogos Gerados (Garantia de 14pts)</div>
                        <div class="stat-value" id="qtdJogos" style="color: var(--primary); font-size: 2.5rem;">--</div>
                    </div>
                    <div>
                        <div class="stat-desc">Custo do Fechamento</div>
                        <div class="stat-value" id="custoJogos" style="font-size: 2.5rem;">R$ --</div>
                    </div>
                    <div>
                        <div class="stat-desc">Economia Imediata vs Jogo Completo</div>
                        <div class="stat-highlight" id="economiaJogos">R$ --</div>
                    </div>
                </div>
            </div>
            
            <h3 style="color: var(--text-main); margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                📋 Volantes para preencher na lotérica:
                <button class="btn" onclick="exportarTXT()" style="background: var(--secondary); font-size: 0.9rem; padding: 8px 15px; width: auto;">⬇️ Baixar .TXT</button>
            </h3>
            <div class="volante-grid" id="volanteGrid">
                <!-- Jogos gerados via JS -->
            </div>
        </div>
    </div>

    <script src="assets/js/fechamento.js?v=<?php echo time(); ?>"></script>
</body>
</html>
