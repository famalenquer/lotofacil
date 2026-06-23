// assets/js/correlacao.js

let dadosCorrelacao = null;

document.addEventListener('DOMContentLoaded', () => {
    popularSelect();
    fetchData();
});

function popularSelect() {
    const select = document.getElementById('dezenaSelect');
    for (let i = 1; i <= 25; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.text = `Dezena ${i.toString().padStart(2, '0')}`;
        select.appendChild(option);
    }
}

async function fetchData() {
    showLoader();
    try {
        const response = await fetch(`api/correlacao.php`);
        const data = await response.json();
        
        if (data.status === 'error') {
            alert('Erro ao carregar dados: ' + data.message);
            hideLoader();
            return;
        }

        dadosCorrelacao = data.parcerias_detalhadas;
        
        renderAlertas(data.alertas);
        renderTopPares(data.top_pares);
        renderDetalheCorrelacao(); // Renderiza a dezena 01 por padrao

    } catch (error) {
        console.error("Erro na requisição:", error);
        alert('Falha na comunicação com o servidor.');
    }
    hideLoader();
}

function renderAlertas(alertas) {
    const container = document.getElementById('alertasContainer');
    container.innerHTML = '';
    
    if (alertas.length === 0) {
        container.innerHTML = '<div style="color:var(--primary);">Nenhuma anomalia estatística detectada nos últimos 100 sorteios. Todas as dezenas estão dentro do desvio padrão esperado.</div>';
        return;
    }
    
    alertas.forEach(alerta => {
        const div = document.createElement('div');
        div.className = `alert-box ${alerta.tipo}`;
        
        const icon = alerta.tipo === 'quente' ? '🔥' : '❄️';
        
        div.innerHTML = `
            <div class="alert-icon">${icon}</div>
            <div>${alerta.mensagem}</div>
        `;
        container.appendChild(div);
    });
}

function renderTopPares(pares) {
    const list = document.getElementById('topParesGlobais');
    list.innerHTML = '';
    
    // O valor máximo para calcular a porcentagem da barra
    const maxVal = pares[0][1];
    
    pares.forEach(par => {
        const nomePar = par[0];
        const count = par[1];
        const pct = (count / maxVal) * 100;
        
        list.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span style="font-weight:bold; color:var(--primary);">${nomePar}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">${count} vezes juntos</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background: var(--primary);"></div>
                </div>
            </li>
        `;
    });
}

function renderDetalheCorrelacao() {
    if (!dadosCorrelacao) return;
    
    const select = document.getElementById('dezenaSelect');
    const dezena = select.value;
    const detalhes = dadosCorrelacao[dezena];
    
    const container = document.getElementById('detalheCorrelacao');
    container.innerHTML = '';
    
    // Card Bons Parceiros
    let htmlBons = `<div class="corr-card">
        <span class="main-dezena">${dezena.toString().padStart(2, '0')}</span>
        <div style="margin-bottom:10px; color:var(--text-muted);">Sai mais junto com:</div>
        <div>`;
    detalhes.top_parceiros.forEach(num => {
        htmlBons += `<span class="corr-badge bg-good">${num.toString().padStart(2, '0')}</span>`;
    });
    htmlBons += `</div></div>`;
    
    // Card Maus Parceiros
    let htmlMaus = `<div class="corr-card">
        <span class="main-dezena">${dezena.toString().padStart(2, '0')}</span>
        <div style="margin-bottom:10px; color:var(--text-muted);">Evita sair com:</div>
        <div>`;
    detalhes.piores_parceiros.forEach(num => {
        htmlMaus += `<span class="corr-badge bg-bad">${num.toString().padStart(2, '0')}</span>`;
    });
    htmlMaus += `</div></div>`;
    
    container.innerHTML = htmlBons + htmlMaus;
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
