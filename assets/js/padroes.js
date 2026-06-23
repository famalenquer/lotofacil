// assets/js/padroes.js

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    showLoader();
    try {
        const response = await fetch(`api/padroes_avancados.php`);
        const data = await response.json();
        
        if (data.status === 'error') {
            alert('Erro ao carregar dados: ' + data.message);
            hideLoader();
            return;
        }

        renderCiclo(data.ciclo);
        renderMoldura(data.moldura);

    } catch (error) {
        console.error("Erro na requisição:", error);
        alert('Falha na comunicação com o servidor.');
    }
    hideLoader();
}

function renderCiclo(ciclo) {
    document.getElementById('cicloAtual').innerText = ciclo.numero_ciclo_atual;
    document.getElementById('concursosRodados').innerText = ciclo.concursos_rodados;
    document.getElementById('mediaCiclo').innerText = ciclo.tamanho_medio_historico;
    
    const missingContainer = document.getElementById('missingBalls');
    missingContainer.innerHTML = '';
    
    if (ciclo.dezenas_faltantes.length === 0) {
        missingContainer.innerHTML = '<div style="color: var(--primary); font-weight:bold; font-size:1.2rem;">Ciclo fechado no último sorteio! Um novo ciclo começará no próximo concurso.</div>';
    } else {
        ciclo.dezenas_faltantes.forEach(num => {
            const el = document.createElement('div');
            el.className = 'missing-ball';
            el.innerText = num.toString().padStart(2, '0');
            missingContainer.appendChild(el);
        });
    }

    const drawnContainer = document.getElementById('drawnBalls');
    drawnContainer.innerHTML = '';
    ciclo.dezenas_sorteadas.sort((a,b) => a-b).forEach(num => {
        const el = document.createElement('div');
        el.className = 'drawn-ball';
        el.innerText = num.toString().padStart(2, '0');
        drawnContainer.appendChild(el);
    });
}

function renderMoldura(moldura) {
    document.getElementById('mediaMoldura').innerText = moldura.media_ultimos_100;
    
    const list = document.getElementById('molduraList');
    list.innerHTML = '';
    
    const maxVal = moldura.top_padroes[0][1];
    
    moldura.top_padroes.forEach(item => {
        const padrao = item[0];
        const count = item[1];
        const pct = (count / maxVal) * 100;
        
        list.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span class="rank-badge" style="color: var(--primary); width: 60px;">${padrao}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">${count} vezes</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background: var(--primary);"></div>
                </div>
            </li>
        `;
    });
}

function showLoader() {
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    loader.style.opacity = '0';
    setTimeout(() => { loader.style.display = 'none'; }, 500);
}
