// assets/js/simulador.js

let dezenasSelecionadas = new Set();

document.addEventListener('DOMContentLoaded', () => {
    gerarVolante();
});

function gerarVolante() {
    const volante = document.getElementById('volante');
    volante.innerHTML = '';
    
    for (let i = 1; i <= 25; i++) {
        const btn = document.createElement('button');
        btn.className = 'bola-btn';
        btn.innerText = i.toString().padStart(2, '0');
        btn.onclick = () => toggleDezena(i, btn);
        volante.appendChild(btn);
    }
}

function toggleDezena(num, btnElement) {
    if (dezenasSelecionadas.has(num)) {
        dezenasSelecionadas.delete(num);
        btnElement.classList.remove('selected');
    } else {
        if (dezenasSelecionadas.size >= 20) {
            alert('Você só pode selecionar até 20 dezenas.');
            return;
        }
        dezenasSelecionadas.add(num);
        btnElement.classList.add('selected');
    }
    document.getElementById('contador-bolas').innerText = dezenasSelecionadas.size;
}

function limparVolante() {
    dezenasSelecionadas.clear();
    document.getElementById('contador-bolas').innerText = '0';
    document.querySelectorAll('.bola-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('test-results').style.display = 'none';
}

function setDezenasNoVolante(arrayDezenas) {
    limparVolante();
    const botoes = document.querySelectorAll('.bola-btn');
    arrayDezenas.forEach(num => {
        if(num >= 1 && num <= 25) {
            botoes[num - 1].click(); // Simula o clique para usar a logica padrão
        }
    });
}

async function testarJogo() {
    if (dezenasSelecionadas.size < 15) {
        alert('Selecione pelo menos 15 dezenas para testar.');
        return;
    }
    
    const dezenasArray = Array.from(dezenasSelecionadas).sort((a,b) => a - b);
    const params = new URLSearchParams({ dezenas: dezenasArray.join(',') });
    
    showLoader('Consultando histórico de sorteios...');
    
    try {
        const response = await fetch(`api/run_simulador.php?${params}`);
        const data = await response.json();
        
        if (data.status === 'error') {
            alert('Erro: ' + data.message);
        } else {
            renderTestResults(data);
        }
    } catch (e) {
        alert('Erro ao comunicar com o servidor.');
        console.error(e);
    }
    
    hideLoader();
}

function renderTestResults(data) {
    const box = document.getElementById('test-results');
    const list = document.getElementById('prize-list');
    
    box.style.display = 'block';
    list.innerHTML = `
        <div class="prize-row"><span style="color:var(--primary); font-weight:bold;">15 Acertos:</span> <span>${data.resultados['15']} vezes</span></div>
        <div class="prize-row"><span style="color:var(--secondary); font-weight:bold;">14 Acertos:</span> <span>${data.resultados['14']} vezes</span></div>
        <div class="prize-row"><span style="color:#facc15; font-weight:bold;">13 Acertos:</span> <span>${data.resultados['13']} vezes</span></div>
        <div class="prize-row"><span>12 Acertos:</span> <span>${data.resultados['12']} vezes</span></div>
        <div class="prize-row"><span>11 Acertos:</span> <span>${data.resultados['11']} vezes</span></div>
    `;
}

async function gerarSugestoes() {
    showLoader();
    
    const qtd = document.getElementById('qtdJogos') ? document.getElementById('qtdJogos').value : 3;
    const tamanho = document.getElementById('tamanhoJogo') ? document.getElementById('tamanhoJogo').value : 15;
    
    try {
        const response = await fetch(`api/run_engine.php`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ qtd: qtd, tamanho: tamanho })
        });
        
        const data = await response.json();
        
        if (data.status === 'error') {
            alert('Erro: ' + data.message);
            hideLoader();
            return;
        }
        
        // Dispara o Teste em Lote no histórico
        testarLote(data.sugestoes, data.usa_ml, data.tamanho_gerado);
        
    } catch (e) {
        alert('Erro ao comunicar com o servidor.');
        console.error(e);
        hideLoader();
    }
}

async function testarLote(sugestoes, usa_ml, tamanho) {
    // Monta o payload
    const payload = {
        jogos: sugestoes.map(s => s.dezenas)
    };
    
    try {
        const resp = await fetch('api/run_simulador_lote.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const testData = await resp.json();
        
        if (testData.status === 'success') {
            renderPalpitesLote(sugestoes, usa_ml, tamanho, testData.resultados);
        } else {
            console.error(testData);
            alert("Erro no backtesting: " + testData.message);
        }
        
    } catch (e) {
        console.error(e);
        alert("Erro no backtesting.");
    }
    
    hideLoader();
}

function renderPalpitesLote(sugestoes, usa_ml, tamanho, resultados) {
    const container = document.getElementById('ia-results');
    container.innerHTML = '';
    
    sugestoes.forEach((sugestao, index) => {
        const card = document.createElement('div');
        card.className = 'sugestao-card';
        
        let bolasHtml = '';
        sugestao.dezenas.forEach(d => {
            const z = d.toString().padStart(2, '0');
            bolasHtml += `<span style="display:inline-block; width:30px; height:30px; background:var(--bg-color); border:1px solid var(--secondary); border-radius:50%; text-align:center; line-height:28px; margin:2px; font-weight:bold;">${z}</span>`;
        });
        
        const badgeMl = usa_ml ? '<span style="background:var(--primary); color:#1a1025; font-size:0.7rem; padding:2px 6px; border-radius:4px; font-weight:bold; margin-left:10px;">🤖 ML Ativo</span>' : '';
        const badgeTam = `<span style="background:var(--text-muted); color:#1a1025; font-size:0.7rem; padding:2px 6px; border-radius:4px; font-weight:bold; margin-left:10px;">${tamanho} Dezenas</span>`;
        
        const result = resultados.find(r => r.index === index);
        const acertosHtml = result ? `
            <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px;">
                <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 5px;">🏆 Validação no Histórico Real (3000+ Sorteios):</div>
                <div style="display:flex; justify-content:space-between; text-align:center;">
                    <div><span style="color:#10b981; font-weight:bold;">${result.acertos_15}</span>x<br><small>15 Pts</small></div>
                    <div><span style="color:#3b82f6; font-weight:bold;">${result.acertos_14}</span>x<br><small>14 Pts</small></div>
                    <div><span style="color:#facc15; font-weight:bold;">${result.acertos_13}</span>x<br><small>13 Pts</small></div>
                </div>
            </div>
        ` : '';
        
        card.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;">
                <div><strong style="color:var(--text-main);">Palpite ${index + 1}</strong> ${badgeMl} ${badgeTam}</div>
                <span style="color:var(--primary); font-weight:bold;">Score IA: ${sugestao.eficiencia}%</span>
            </div>
            <div>${bolasHtml}</div>
            ${acertosHtml}
            <div style="margin-top:10px; text-align:right;">
                <button class="btn" style="width: auto; padding: 5px 15px; font-size: 0.8rem;" onclick='setDezenasNoVolante(${JSON.stringify(sugestao.dezenas)})'>✍️ Passar pro Volante Lateral</button>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function showLoader(text) {
    document.getElementById('loader-text').innerText = text;
    document.getElementById('loader').style.display = 'flex';
    setTimeout(() => { document.getElementById('loader').style.opacity = '1'; }, 10);
}

function hideLoader() {
    const loader = document.getElementById('loader');
    loader.style.opacity = '0';
    setTimeout(() => { loader.style.display = 'none'; }, 500);
}
