window.gameStates = {};

async function analisarJogo(id) {
    const box = document.getElementById(`analise-${id}`);
    
    if (box.style.display === 'block') {
        box.style.display = 'none';
        return;
    }
    
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
    
    try {
        const response = await fetch(`api/analisar_jogo.php?id=${id}`);
        const data = await response.json();
        
        if (data.status === 'error') throw new Error(data.message);
        
        window.gameStates[id] = {
            original: JSON.parse(JSON.stringify(data)),
            atual: JSON.parse(JSON.stringify(data))
        };
        
        renderizarAnalise(id);
    } catch (e) {
        console.error(e);
        alert("Erro ao conferir o jogo: " + e.message);
    } finally {
        const loader = document.getElementById('loader');
        loader.style.opacity = '0';
        setTimeout(() => { loader.style.display = 'none'; }, 300);
    }
}

function renderizarAnalise(id) {
    const box = document.getElementById(`analise-${id}`);
    const data = window.gameStates[id].atual;
    const isSimulacao = JSON.stringify(window.gameStates[id].atual) !== JSON.stringify(window.gameStates[id].original);
    
    let html = '';
    if (isSimulacao) {
        html += `<h4 style="color: #f59e0b; margin-top:0;">⚠️ MODO SIMULAÇÃO "E SE..." (Concurso ${data.concurso_analisado})</h4>`;
    } else {
        html += `<h4 style="color: var(--primary); margin-top:0;">Resultado Original: Concurso ${data.concurso_analisado}</h4>`;
    }
    
    html += `<div style="margin-bottom: 15px;"><strong>Dezenas Sorteadas:</strong><br>`;
    data.sorteadas.forEach(n => {
        let isNewHit = isSimulacao && !window.gameStates[id].original.sorteadas.includes(n);
        let bolaStyle = isNewHit ? 'background: #f59e0b; border-color: #d97706; color: #fff;' : '';
        html += `<span class="dezena-bola hit" style="${bolaStyle}">${n.toString().padStart(2, '0')}</span>`;
    });
    html += `</div>`;
    
    html += `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">`;
    html += `<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; text-align: center;">
                Acertos nas Fixas<br>
                <strong style="font-size: 1.5rem; color: #fbbf24;">${data.acertos_fixas} / ${data.total_fixas}</strong>
             </div>`;
    html += `<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px; text-align: center;">
                Sorteados dentro da Base<br>
                <strong style="font-size: 1.5rem; color: #10b981;">${data.acertos_base} / 15</strong>
             </div>`;
    html += `</div>`;
    
    html += `<h5>Desempenho por Bilhete</h5>`;
    html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; margin-bottom: 20px;">`;
    data.volantes_analisados.forEach(v => {
        let bgColor = 'rgba(255,255,255,0.02)';
        let borderColor = 'rgba(255,255,255,0.1)';
        let textColor = 'var(--text-muted)';
        
        if (v.acertos <= 8) { bgColor = 'rgba(255,255,255,0.01)'; borderColor = 'rgba(255,255,255,0.05)'; textColor = 'var(--text-muted)'; }
        else if (v.acertos === 9) { bgColor = 'rgba(255,255,255,0.03)'; borderColor = 'rgba(255,255,255,0.1)'; textColor = '#9ca3af'; }
        else if (v.acertos === 10) { bgColor = 'rgba(251, 191, 36, 0.05)'; borderColor = 'rgba(251, 191, 36, 0.2)'; textColor = '#d1d5db'; }
        else if (v.acertos === 11) { bgColor = 'rgba(16, 185, 129, 0.1)'; borderColor = '#10b981'; textColor = '#10b981'; }
        else if (v.acertos === 12) { bgColor = 'rgba(59, 130, 246, 0.1)'; borderColor = '#3b82f6'; textColor = '#3b82f6'; }
        else if (v.acertos === 13) { bgColor = 'rgba(168, 85, 247, 0.1)'; borderColor = '#a855f7'; textColor = '#a855f7'; }
        else if (v.acertos === 14) { bgColor = 'rgba(249, 115, 22, 0.1)'; borderColor = '#f97316'; textColor = '#f97316'; }
        else if (v.acertos === 15) { bgColor = 'rgba(234, 179, 8, 0.2)'; borderColor = '#eab308'; textColor = '#eab308'; }

        let htmlBolas = '';
        v.numeros.forEach(num => {
            let isHit = data.sorteadas.includes(num);
            let extraClass = isHit ? 'hit' : '';
            htmlBolas += `<span class="dezena-bola ${extraClass}" style="width: 22px; height: 22px; line-height: 20px; font-size: 0.75rem; margin: 1px;">${num.toString().padStart(2,'0')}</span>`;
        });

        let premioText = v.premio > 0 ? `<br><small style="color: #fbbf24; font-weight: bold;">+ R$ ${v.premio.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</small>` : '';
        html += `<div style="background: ${bgColor}; border: 1px solid ${borderColor}; padding: 10px; border-radius: 5px; text-align: center; transition: 0.2s;">
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px;">Jogo ${v.jogo}</div>
                    <div style="line-height: 1.2;">${htmlBolas}</div>
                    <div style="margin-top: 10px;">
                        <strong style="color: ${textColor}; font-size: 1.1rem;">${v.acertos} acertos</strong>${premioText}
                    </div>
                 </div>`;
    });
    html += `</div>`;
    
    // Atualiza base visual (não muda estrutura no PHP, só cores JS)
    const baseBox = document.getElementById(`base-${id}`);
    if (baseBox) {
        baseBox.querySelectorAll('.dezena-bola').forEach(bola => {
            const num = parseInt(bola.getAttribute('data-num'));
            if (data.sorteadas.includes(num)) bola.classList.add('hit');
            else bola.classList.remove('hit');
        });
    }
    const fixasBox = document.getElementById(`fixas-${id}`);
    if (fixasBox) {
        fixasBox.querySelectorAll('.dezena-bola').forEach(bola => {
            const num = parseInt(bola.getAttribute('data-num'));
            if (data.sorteadas.includes(num)) bola.classList.add('hit');
            else bola.classList.remove('hit');
        });
    }
    
    html += `<h5>Premiações (Simulação)</h5>`;
    let temPremio = false;
    
    for (let pt = 15; pt >= 11; pt--) {
        const info = data.premios[pt];
        if (info.qtd > 0) {
            temPremio = true;
            const totalLinha = info.qtd * info.valor;
            html += `<div class="prize-row">
                        <span>${info.qtd}x cartões com ${pt} pontos</span>
                        <span style="color: #10b981;">R$ ${totalLinha.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
                     </div>`;
        }
    }
    
    if (!temPremio) {
        html += `<div class="prize-row" style="color: var(--text-muted); justify-content: center;">Nenhum bilhete premiado.</div>`;
    }
    
    const lucroClass = data.lucro >= 0 ? 'lucro-positivo' : 'lucro-negativo';
    html += `<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2); display: flex; justify-content: space-between; align-items: center;">
                <strong>Retorno Financeiro Líquido:</strong>
                <span class="${lucroClass}" style="font-size: 1.2rem;">R$ ${data.lucro.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
             </div>`;

    if (!data.concurso_alvo_salvo && !isSimulacao) {
        html += `<div style="margin-top: 15px; text-align: center;">
                    <button class="btn" onclick="travarResultado(${id}, ${data.concurso_analisado})" style="background: #10b981; border: none; padding: 10px 20px; font-size: 1rem;">
                        💾 Salvar Resultado (Concurso ${data.concurso_analisado})
                    </button>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 5px;">Ao salvar, este jogo ficará permanentemente associado a este sorteio.</p>
                 </div>`;
    }

    if (!isSimulacao && data.diagnosticos_ia && data.diagnosticos_ia.length > 0) {
        html += `<div style="margin-top: 25px; margin-bottom: 25px;">
                    <h4 style="color: #a855f7; margin-bottom: 15px; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 10px;">🤖 Laudo Avançado da IA</h4>
                    <div style="display: flex; flex-direction: column; gap: 10px;">`;
                    
        data.diagnosticos_ia.forEach(diag => {
            let bg, border, color, icon;
            if (diag.tipo === 'danger') { bg = 'rgba(239, 68, 68, 0.05)'; border = '#ef4444'; color = '#ef4444'; icon = '🚨'; }
            else if (diag.tipo === 'warning') { bg = 'rgba(245, 158, 11, 0.05)'; border = '#f59e0b'; color = '#f59e0b'; icon = '⚠️'; }
            else if (diag.tipo === 'success') { bg = 'rgba(16, 185, 129, 0.05)'; border = '#10b981'; color = '#10b981'; icon = '✅'; }
            else { bg = 'rgba(59, 130, 246, 0.05)'; border = '#3b82f6'; color = '#3b82f6'; icon = '💡'; }
            
            html += `<div style="background: ${bg}; border: 1px solid rgba(255,255,255,0.05); border-left: 4px solid ${border}; border-radius: 4px; padding: 12px;">
                        <h6 style="color: ${color}; margin-top: 0; margin-bottom: 8px; font-size: 1rem; font-weight: bold;">${icon} ${diag.titulo}</h6>
                        <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.4; margin: 0;">${diag.mensagem}</p>
                     </div>`;
        });
        
        html += `   </div>
                 </div>`;
    }

    // Painel E se...
    html += renderizarPainelESe(id);

    box.innerHTML = html;
    box.style.display = 'block';
}

function renderizarPainelESe(id) {
    const data = window.gameStates[id].atual;
    
    // Dezenas erradas (estão na base mas não nas sorteadas)
    const dezenasErradas = data.dezenas_base.filter(n => !data.sorteadas.includes(n));
    // Dezenas sorteadas não escolhidas
    const sorteadasNaoEscolhidas = data.sorteadas.filter(n => !data.dezenas_base.includes(n));
    
    if (dezenasErradas.length === 0 || sorteadasNaoEscolhidas.length === 0) {
        return `<div style="margin-top: 20px; color: var(--text-muted); text-align: center;">(Jogo 100% perfeito ou impossível de simular mais trocas válidas)</div>`;
    }

    let optionsErradas = dezenasErradas.map(n => `<option value="${n}">${String(n).padStart(2,'0')}</option>`).join('');
    let optionsSorteadas = sorteadasNaoEscolhidas.map(n => `<option value="${n}">${String(n).padStart(2,'0')}</option>`).join('');

    return `
    <div style="margin-top: 25px; background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 15px;">
        <h5 style="color: #f59e0b; margin-top: 0; margin-bottom: 10px;">🔄 Modo Simulação "E se..."</h5>
        <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 15px;">E se no lugar da dezena que você errou, tivesse escolhido uma dezena que saiu? Faça a troca e veja o impacto instantâneo nos seus bilhetes e prêmios!</p>
        
        <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
            <div>
                <label style="font-size: 0.8rem; color: var(--text-muted); display: block; margin-bottom: 5px;">Dezena que você errou:</label>
                <select id="sim-old-${id}" style="background: rgba(0,0,0,0.2); border: 1px solid var(--card-border); color: #ef4444; padding: 8px; border-radius: 4px; font-weight: bold;">
                    ${optionsErradas}
                </select>
            </div>
            
            <span style="color: var(--text-muted);">👉 trocar por 👉</span>
            
            <div>
                <label style="font-size: 0.8rem; color: var(--text-muted); display: block; margin-bottom: 5px;">Dezena sorteada:</label>
                <select id="sim-new-${id}" style="background: rgba(0,0,0,0.2); border: 1px solid var(--card-border); color: #10b981; padding: 8px; border-radius: 4px; font-weight: bold;">
                    ${optionsSorteadas}
                </select>
            </div>
            
            <div style="margin-top: 15px;">
                <button class="btn" onclick="executarSimulacao(${id})" style="background: #f59e0b; padding: 8px 15px; border-radius: 5px; color: #fff;">Simular Troca!</button>
                <button class="btn" onclick="resetarSimulacao(${id})" style="background: transparent; border: 1px solid var(--card-border); padding: 8px 15px; border-radius: 5px; color: var(--text-muted); margin-left: 5px;">Desfazer Tudo</button>
            </div>
        </div>
    </div>
    `;
}

function executarSimulacao(id) {
    const oldNum = parseInt(document.getElementById(`sim-old-${id}`).value);
    const newNum = parseInt(document.getElementById(`sim-new-${id}`).value);
    
    let state = window.gameStates[id].atual;
    
    // Atualiza base e fixas
    if (state.dezenas_base.includes(oldNum)) {
        state.dezenas_base[state.dezenas_base.indexOf(oldNum)] = newNum;
    }
    if (state.dezenas_fixas.includes(oldNum)) {
        state.dezenas_fixas[state.dezenas_fixas.indexOf(oldNum)] = newNum;
    }
    
    // Recalcula volantes
    state.valor_ganho = 0;
    // Reseta premissas de prêmio
    Object.keys(state.premios).forEach(pt => {
        state.premios[pt].qtd = 0;
    });

    state.volantes_analisados.forEach(v => {
        // Substitui dezena se existir
        if (v.numeros.includes(oldNum)) {
            v.numeros[v.numeros.indexOf(oldNum)] = newNum;
        }
        
        // Re-analisa acertos
        v.acertos = v.numeros.filter(n => state.sorteadas.includes(n)).length;
        
        v.premio = 0;
        if (v.acertos >= 11 && v.acertos <= 15) {
            state.premios[v.acertos].qtd++;
            state.premios[v.acertos].valor = state.premios[v.acertos].valor; // mantém tabela
            state.valor_ganho += state.premios[v.acertos].valor;
            v.premio = state.premios[v.acertos].valor;
        }
    });
    
    state.lucro = state.valor_ganho - state.custo;
    state.acertos_base = state.dezenas_base.filter(n => state.sorteadas.includes(n)).length;
    state.acertos_fixas = state.dezenas_fixas.filter(n => state.sorteadas.includes(n)).length;

    renderizarAnalise(id);
}

function resetarSimulacao(id) {
    window.gameStates[id].atual = JSON.parse(JSON.stringify(window.gameStates[id].original));
    renderizarAnalise(id);
}

async function excluirJogo(id) {
    if (!confirm("Tem certeza que deseja excluir este jogo salvo? Esta ação não pode ser desfeita.")) {
        return;
    }
    
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
    
    try {
        const response = await fetch(`api/excluir_jogo.php?id=${id}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.status === 'success') {
            const card = document.getElementById(`jogo-${id}`);
            card.style.opacity = '0';
            setTimeout(() => { card.remove(); }, 300);
        } else {
            throw new Error(data.message);
        }
    } catch (e) {
        console.error(e);
        alert("Erro ao excluir: " + e.message);
    } finally {
        const loader = document.getElementById('loader');
        loader.style.opacity = '0';
        setTimeout(() => { loader.style.display = 'none'; }, 300);
    }
}

async function travarResultado(id, concurso) {
    if (!confirm(`Deseja travar este jogo no Concurso ${concurso}? Ao fazer isso, o resultado ficará salvo permanentemente.`)) {
        return;
    }
    
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
    
    try {
        const payload = { id: id, concurso_alvo: concurso };
        const response = await fetch('api/travar_resultado.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            alert("✅ Resultado salvo com sucesso!");
            window.location.reload(); // Reload to update button states
        } else {
            throw new Error(data.message);
        }
    } catch (e) {
        console.error(e);
        alert("Erro ao salvar resultado: " + e.message);
    } finally {
        const loader = document.getElementById('loader');
        loader.style.opacity = '0';
        setTimeout(() => { loader.style.display = 'none'; }, 300);
    }
}
