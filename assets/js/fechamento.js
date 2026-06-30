async function gerarFechamento() {
    showLoader();
    
    // Timeout forçado de 15 segundos para evitar que o navegador trave
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
        const strategy = document.getElementById('strategySelect').value;
        const cacheBuster = new Date().getTime();
        const response = await fetch(`api/run_fechamento.php?strategy=${strategy}&t=${cacheBuster}`, {
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        clearTimeout(timeoutId);
        const text = await response.text();
        
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error("Erro no Parse JSON. Resposta Bruta:", text);
            hideLoader();
            alert('Falha interna do servidor: A resposta não é um JSON válido. Verifique os logs.');
            return;
        }
        
        if (data.status === 'error') {
            hideLoader();
            alert('Erro reportado pelo Motor: ' + data.message);
            return;
        }

        renderResultados(data);
        hideLoader();
    } catch (error) {
        clearTimeout(timeoutId);
        console.error("Erro na requisição:", error);
        hideLoader();
        
        if (error.name === 'AbortError') {
            setTimeout(() => alert('Tempo Limite Esgotado! O servidor demorou mais de 15 segundos para responder. Tente novamente.'), 500);
        } else {
            setTimeout(() => alert('Falha grave na comunicação com o servidor. Tente atualizar a página.'), 500);
        }
    }
}

function renderResultados(data) {
    document.getElementById('resultados').style.display = 'block';
    
    // Atualiza Textos Dinâmicos de Resultado
    const baseCount = data.dezenas_base.length;
    document.getElementById('resultadosTituloBase').innerText = `As ${baseCount} Dezenas Base Selecionadas pela IA`;
    
    let garantiaTexto = "Garantia de 14pts";
    if (baseCount >= 19 || document.getElementById('strategySelect').value === 'economico') {
        garantiaTexto = "Garantia de 13pts";
    } else if (document.getElementById('strategySelect').value === 'filtro_ia') {
        garantiaTexto = "Alta Probabilidade (sem garantia absoluta)";
    }
    document.getElementById('resultadosGarantia').innerText = `Jogos Gerados (${garantiaTexto})`;
    
    // Render Dezenas Base
    const baseContainer = document.getElementById('dezenasBase');
    baseContainer.innerHTML = '';
    const fixas = data.dezenas_fixas || [];
    data.dezenas_base.forEach(num => {
        const el = document.createElement('div');
        el.className = 'dezena-base';
        if (fixas.includes(num)) {
            el.style.background = 'linear-gradient(135deg, #fbbf24, #b45309)';
            el.style.border = '2px solid #fef08a';
            el.title = 'Dezena Fixa';
        }
        el.innerText = num.toString().padStart(2, '0');
        baseContainer.appendChild(el);
    });
    
    // Render Dados Financeiros
    document.getElementById('qtdJogos').innerText = data.quantidade_jogos;
    document.getElementById('dezenasBase').innerText = data.dezenas_base.map(n => n.toString().padStart(2, '0')).join(' ');
    
    const custo = parseFloat(data.quantidade_jogos * 3.50).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    document.getElementById('custoJogos').innerText = `R$ ${custo}`;
    
    const econ = parseFloat(data.economia_reais).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    document.getElementById('economiaJogos').innerText = `R$ ${econ}`;
    
    // Mensagem da Faca da IA
    const msgIa = document.getElementById('msgFiltroIa') || document.createElement('div');
    msgIa.id = 'msgFiltroIa';
    msgIa.style.color = 'var(--danger)';
    msgIa.style.marginTop = '15px';
    msgIa.style.fontWeight = 'bold';
    if (data.msg_filtro) {
        msgIa.innerText = "🤖 " + data.msg_filtro;
    } else {
        msgIa.innerText = "";
    }
    document.getElementById('resultados').insertBefore(msgIa, document.getElementById('volanteGrid'));
    
    // Salva globalmente para exportação e para salvar no BD
    const select = document.getElementById('strategySelect');
    window.lastGeneratedData = {
        nome_estrategia: select.options[select.selectedIndex].text.split(':')[0],
        dezenas_base: data.dezenas_base,
        dezenas_fixas: data.dezenas_fixas || [],
        jogos: data.jogos,
        qtd_jogos: data.quantidade_jogos,
        custo: data.quantidade_jogos * 3.50
    };
    window.lastGeneratedGames = data.jogos;

    
    // Render Volantes
    const grid = document.getElementById('volanteGrid');
    grid.innerHTML = '';
    
    data.jogos.forEach((jogo, idx) => {
        const card = document.createElement('div');
        card.className = 'volante-card';
        
        let bolas = '';
        const fixas = data.dezenas_fixas || [];
        jogo.forEach(num => {
            const style = fixas.includes(num) ? 'background: #ca8a04; color: white; border-color: #facc15;' : '';
            bolas += `<span class="volante-bola" style="${style}">${num.toString().padStart(2, '0')}</span>`;
        });
        
        card.innerHTML = `
            <div style="margin-bottom: 10px; font-weight:bold; color:var(--text-muted);">
                Bilhete ${idx + 1}
            </div>
            <div>${bolas}</div>
        `;
        grid.appendChild(card);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('strategySelect');
    const hint = document.getElementById('strategyHint');
    const topDesc = document.getElementById('strategyTopDesc');
    
    if (select) {
        select.addEventListener('change', (e) => {
            if (e.target.value === 'normal') {
                hint.innerText = "Garantia matemática absoluta de 14 pontos. Maior rede de proteção possível.";
                topDesc.innerHTML = "Este algoritmo extrai as <strong>18 dezenas mais poderosas</strong> indicadas pela Inteligência Artificial. A Teoria dos Conjuntos reduz seus bilhetes para garantir <strong>14 Pontos</strong> gastando o mínimo absoluto.";
            } else if (e.target.value === 'economico') {
                hint.innerText = "Garantia matemática de 13 pontos. Ideal para reduzir drasticamente o investimento.";
                topDesc.innerHTML = "Este algoritmo extrai as <strong>18 dezenas mais poderosas</strong>. O fechamento reduz seus bilhetes focando em garantir <strong>13 Pontos</strong> com o menor custo possível.";
            } else if (e.target.value === 'filtro_ia') {
                hint.innerText = "Destrói bilhetes matemáticos que não se alinham ao Clima de hoje. Perde a garantia 100%, mas foca na alta probabilidade.";
                topDesc.innerHTML = "O algoritmo gera as combinações das <strong>18 dezenas</strong> e aplica os filtros avançados da IA (Pares/Ímpares, Moldura, Soma) para cortar jogos improváveis e baratear o custo.";
            } else if (e.target.value === 'diamante_economico') {
                hint.innerText = "Base enorme de 19 Dezenas. Trava 3 Dezenas Fixas de Ouro e garante 13 pontos se as fixas baterem.";
                topDesc.innerHTML = "O algoritmo expande o universo para <strong>19 dezenas</strong>. Ao cravar <strong>3 fixas</strong>, o modelo de Teoria dos Conjuntos reduz drasticamente o custo mantendo a garantia de <strong>13 Pontos</strong>.";
            } else if (e.target.value === 'diamante_supremo') {
                hint.innerText = "Joga apenas 5 números fora! 20 Dezenas com 3 Fixas de Ouro. Garante 13 pontos se as fixas baterem.";
                topDesc.innerHTML = "O fechamento mais abrangente: <strong>20 dezenas base</strong>. Com apenas <strong>3 fixas</strong>, você elimina quase o risco de errar as dezenas e busca <strong>13 Pontos</strong> de forma suprema.";
            }
        });
        // Dispara o evento na inicialização para ajustar ao padrão caso esteja cacheado
        select.dispatchEvent(new Event('change'));
    }
});

function showLoader() {
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    loader.style.opacity = '0';
    setTimeout(() => { loader.style.display = 'none'; }, 500);
}

function exportarTXT() {
    if (!window.lastGeneratedGames || window.lastGeneratedGames.length === 0) {
        alert("Nenhum jogo gerado para exportar!");
        return;
    }
    
    let txtContent = "Lotofácil Pro Analytics - Fechamento Matemático\n";
    txtContent += "==============================================\n\n";
    
    window.lastGeneratedGames.forEach((jogo, index) => {
        const linha = jogo.map(n => n.toString().padStart(2, '0')).join(" ");
        txtContent += `Jogo ${String(index + 1).padStart(2, '0')}: ${linha}\n`;
    });
    
    const blob = new Blob([txtContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `Fechamento_Lotofacil_${window.lastGeneratedGames.length}_jogos.txt`;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

async function salvarJogo() {
    if (!window.lastGeneratedData) {
        alert("Nenhum jogo gerado para salvar!");
        return;
    }
    
    const btn = document.getElementById('btnSalvarJogo');
    const originalText = btn.innerHTML;
    btn.innerHTML = '⏳ Salvando...';
    btn.disabled = true;
    
    try {
        const response = await fetch('api/salvar_jogo.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(window.lastGeneratedData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            btn.innerHTML = '✅ Salvo!';
            btn.style.background = '#059669';
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = '#10b981';
                btn.disabled = false;
            }, 3000);
        } else {
            throw new Error(data.message);
        }
    } catch (e) {
        console.error(e);
        alert("Erro ao salvar o jogo: " + e.message);
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

