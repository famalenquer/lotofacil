<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lotofácil Pro - Fechamento Manual</title>
    <link rel="stylesheet" href="assets/css/style.css">
    <style>
        .dezena-seletor {
            display: inline-flex; width: 45px; height: 45px; border-radius: 50%;
            background: rgba(255,255,255,0.05); border: 2px solid rgba(255,255,255,0.2);
            color: rgba(255,255,255,0.7); font-weight: bold; font-size: 1.2rem;
            align-items: center; justify-content: center;
            cursor: pointer; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            user-select: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .dezena-seletor:hover {
            transform: scale(1.15) translateY(-2px);
            background: rgba(255,255,255,0.15);
            color: #fff;
            border-color: rgba(255,255,255,0.5);
            box-shadow: 0 8px 15px rgba(0,0,0,0.3);
        }
        .dezena-seletor.selected-base {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            border-color: #93c5fd; color: #fff;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.6), inset 0 2px 4px rgba(255,255,255,0.3);
            transform: scale(1.05);
        }
        .dezena-seletor.selected-fixa {
            background: linear-gradient(135deg, #facc15, #ca8a04);
            border-color: #fef08a; color: #1a1025;
            box-shadow: 0 0 15px rgba(250, 204, 21, 0.6), inset 0 2px 4px rgba(255,255,255,0.5);
            transform: scale(1.05);
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

        .volante-seletor-container {
            max-width: 360px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            padding: 25px;
            background: linear-gradient(145deg, rgba(20,20,30,0.8), rgba(0,0,0,0.4));
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        
        .legenda {
            display: flex; justify-content: center; gap: 20px; margin-top: 20px;
            font-size: 0.9rem; color: var(--text-muted);
            background: rgba(0,0,0,0.2); padding: 10px 20px; border-radius: 20px;
            display: inline-flex;
        }
        .legenda-item { display: flex; align-items: center; gap: 8px; }
        .legenda-color { width: 18px; height: 18px; border-radius: 50%; box-shadow: inset 0 2px 4px rgba(255,255,255,0.2); }
        .bg-base { background: linear-gradient(135deg, #3b82f6, #2563eb); border: 1px solid #93c5fd; }
        .bg-fixa { background: linear-gradient(135deg, #facc15, #ca8a04); border: 1px solid #fef08a; }
    </style>
</head>
<body>

    <div class="loader-wrapper" id="loader" style="display:none; opacity:0;">
        <div style="text-align:center;">
            <div class="loader" style="margin: 0 auto 15px auto;"></div>
            <p id="loader-text" style="color: var(--primary);">O algoritmo de Otimização (Set Cover) está calculando a menor matriz matemática possível com as SUAS dezenas...</p>
        </div>
    </div>

    <?php include 'header.php'; ?>

    <div class="container">
        <div class="card" style="margin-bottom: 20px; text-align: center;">
            <p class="stat-desc" style="font-size: 1.1rem; max-width: 800px; margin: 0 auto;">
                <strong>Fechamento Manual:</strong> Você escolhe as dezenas e o sistema aplica a matemática. Selecione a estratégia e preencha o volante abaixo.
            </p>
            <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin-bottom: 20px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1);">
                <select id="strategySelect" onchange="atualizarRegras()" style="width: 100%; padding: 10px; border-radius: 5px; background: #1a1f2e; color: white; border: 1px solid var(--primary); font-size: 1rem; cursor: pointer;">
                    <option value="normal">🎯 Normal: 24 Jogos (Custo: R$ 84,00 | Garantia 14 pts: 100%) - Requer 18 dezenas</option>
                    <option value="economico">💸 Econômico: ~6 Jogos (Custo: R$ 21,00 | Garantia 13 pts: 100%) - Requer 18 dezenas</option>
                    <option value="diamante_economico">💎 Diamante Econômico: 19 Dezenas c/ 3 Fixas (Custo: ~R$ 35,00 | Garantia 13 pts)</option>
                    <option value="diamante_supremo">👑 Diamante Supremo: 20 Dezenas c/ 3 Fixas (Custo: ~R$ 87,50 | Garantia 13 pts)</option>
                </select>
                <div style="margin-top: 15px; padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 5px; border: 1px solid rgba(59, 130, 246, 0.3);">
                    <p id="statusSelecao" style="font-size: 1rem; color: #60a5fa; margin: 0;">Carregando...</p>
                </div>
            </div>

            <div class="volante-seletor-container" id="volanteInterativo">
                <!-- Javascript will generate 25 buttons here -->
            </div>
            
            <div class="legenda">
                <div class="legenda-item"><div class="legenda-color bg-base"></div> Dezena Variável</div>
                <div class="legenda-item" id="legendaFixa" style="display:none;"><div class="legenda-color bg-fixa"></div> Dezena Fixa (obrigatória em todos os jogos)</div>
            </div>
            
            <div style="margin-top: 30px; display: flex; justify-content: center; gap: 20px; align-items: center;">
                <button class="btn" onclick="limparVolante()" style="background: linear-gradient(135deg, #ef4444, #b91c1c); border: none; padding: 12px 25px; font-size: 1rem; border-radius: 8px; width: auto; box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3);">🗑️ Limpar</button>
                <button class="btn" onclick="gerarFechamentoManual()" id="btnGerar" style="background: linear-gradient(135deg, #10b981, #059669); border: none; padding: 12px 40px; font-size: 1.1rem; font-weight: bold; border-radius: 8px; width: auto; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);" disabled>⚙️ Processar Matriz</button>
            </div>
        </div>
        
        <div id="resultados" style="display: none;">
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-title" id="resultadosTituloBase" style="text-align: center;">Suas Dezenas Selecionadas</div>
                <div id="dezenasBase" style="text-align: center; margin: 20px 0;"></div>
                
                <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 30px; border-top: 1px solid var(--card-border); padding-top: 20px;">
                    <div>
                        <div class="stat-desc" id="resultadosGarantia">Jogos Gerados (Garantia Máxima)</div>
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
                📋 Volantes gerados (Prontos para jogar):
                <div style="display: flex; gap: 10px;">
                    <button class="btn" onclick="salvarJogo()" id="btnSalvarJogo" style="background: #10b981; font-size: 0.9rem; padding: 8px 15px; width: auto; border: none;">💾 Salvar Meu Jogo</button>
                    <button class="btn" onclick="exportarTXT()" style="background: var(--secondary); font-size: 0.9rem; padding: 8px 15px; width: auto; border: none;">⬇️ Baixar .TXT</button>
                </div>
            </h3>
            <div class="volante-grid" id="volanteGrid">
                <!-- Jogos gerados via JS -->
            </div>
        </div>
    </div>

    <script src="assets/js/fechamento_manual.js?v=<?php echo time(); ?>"></script>
</body>
</html>
