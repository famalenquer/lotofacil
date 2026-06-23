// assets/js/records.js

document.addEventListener('DOMContentLoaded', carregarRecordes);

async function carregarRecordes() {
    try {
        const response = await fetch(`api/run_historico.php`);
        const text = await response.text();
        
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error(text);
            alert("Falha no servidor ao ler recordes.");
            return;
        }

        if (data.status === 'error') {
            alert('Erro: ' + data.message);
            return;
        }

        renderData(data);
        document.getElementById('loader').style.display = 'none';
        document.getElementById('mainContainer').style.display = 'block';

    } catch (error) {
        console.error(error);
        alert('Falha na comunicação com o servidor.');
    }
}

function renderData(data) {
    // 1. Maior Sequencia
    document.getElementById('maiorSeqNum').innerText = data.maior_sequencia;
    document.getElementById('concursoSeq').innerText = data.concurso_maior_seq;
    
    const seqBolas = document.getElementById('seqBolas');
    data.seq_vencedora.forEach(n => {
        const d = document.createElement('div');
        d.className = 'dezena';
        d.innerText = n.toString().padStart(2, '0');
        seqBolas.appendChild(d);
    });
    
    // 2. Top 5
    const top5 = document.getElementById('top5List');
    data.top_5.forEach((item, index) => {
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.alignItems = 'center';
        row.style.padding = '10px';
        row.style.background = 'rgba(255,255,255,0.05)';
        row.style.borderRadius = '8px';
        
        row.innerHTML = `
            <div style="display:flex; align-items:center; gap:15px;">
                <span style="font-size: 1.5rem; font-weight:bold; color:var(--text-muted);">#${index+1}</span>
                <div class="dezena dezena-quente">${item.dezena.toString().padStart(2, '0')}</div>
            </div>
            <div style="font-size: 1.1rem; font-weight:bold;">${item.freq} vezes</div>
        `;
        top5.appendChild(row);
    });
    
    // 3. Atrasos
    const atrasosList = document.getElementById('atrasosList');
    data.atrasos.forEach(item => {
        const dangerColor = item.risco_quebra ? 'var(--primary)' : 'var(--text-main)';
        const dangerGlow = item.risco_quebra ? 'text-shadow: 0 0 10px var(--primary-glow);' : '';
        const dangerAlert = item.risco_quebra ? '<span style="background:var(--primary); color:#000; padding:2px 8px; border-radius:10px; font-size:0.7rem; font-weight:bold;">TENDÊNCIA DE QUEBRA</span>' : '';
        
        const row = document.createElement('div');
        row.className = 'alert-row';
        row.innerHTML = `
            <div style="display:flex; align-items:center; gap:15px;">
                <div class="dezena">${item.dezena.toString().padStart(2, '0')}</div>
                <div>
                    <div style="font-size:0.9rem; color:var(--text-muted);">Máximo Histórico: ${item.maior_atraso_historico} sorteios</div>
                    <div style="font-size:1.1rem; font-weight:bold; color:${dangerColor}; ${dangerGlow}">Atraso Hoje: ${item.atraso_atual} sorteios ${dangerAlert}</div>
                </div>
            </div>
        `;
        atrasosList.appendChild(row);
    });
}
