// assets/js/cluster.js

function showLoader() {
    document.getElementById('loader').style.display = 'flex';
    document.getElementById('loader').style.opacity = '1';
}

function hideLoader() {
    const loader = document.getElementById('loader');
    loader.style.opacity = '0';
    setTimeout(() => { loader.style.display = 'none'; }, 500);
}

async function analisarClima() {
    showLoader();
    
    try {
        const cacheBuster = new Date().getTime();
        const response = await fetch(`api/run_kmeans.php?t=${cacheBuster}`, {
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error(text);
            alert("Erro fatal ao ler resposta da Inteligência Artificial.");
            hideLoader();
            return;
        }
        
        if (data.status === 'error') {
            alert('Erro: ' + data.message);
            hideLoader();
            return;
        }

        renderResultados(data);
        hideLoader();
    } catch (error) {
        console.error(error);
        alert('Falha na comunicação com o servidor.');
        hideLoader();
    }
}

function renderResultados(data) {
    document.getElementById('resultados').style.display = 'block';
    
    // Identificar clima atual
    const atualId = data.clima_atual;
    const perfilAtual = data.perfis_clusters[atualId];
    
    document.getElementById('climaAtualId').innerText = `Cluster ${atualId}`;
    document.getElementById('climaAtualId').style.color = getClusterColor(atualId);
    
    let desc = `Este clima tem média de ${perfilAtual.media_impares} ímpares e ${perfilAtual.media_moldura} dezenas na moldura.`;
    document.getElementById('climaAtualDesc').innerText = desc;
    
    // Render todos os perfis
    const grid = document.getElementById('clustersGrid');
    grid.innerHTML = '';
    
    Object.keys(data.perfis_clusters).forEach(cId => {
        const p = data.perfis_clusters[cId];
        const isCurrent = parseInt(cId) === atualId;
        
        const card = document.createElement('div');
        card.className = 'card';
        if (isCurrent) {
            card.style.border = '1px solid var(--primary)';
            card.style.boxShadow = '0 0 15px rgba(250, 204, 21, 0.2)';
        }
        
        card.innerHTML = `
            <div class="card-title" style="color: ${getClusterColor(parseInt(cId))};">Cluster ${cId} ${isCurrent ? '⭐' : ''}</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 10px;">Ocorrências Históricas: ${p.qtd_sorteios}</div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;">
                <span>Soma Média</span> <strong>${p.media_soma}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;">
                <span>Ímpares Médios</span> <strong>${p.media_impares}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 5px 0;">
                <span>Primos Médios</span> <strong>${p.media_primos}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                <span>Moldura Média</span> <strong>${p.media_moldura}</strong>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

function getClusterColor(id) {
    const colors = ['#facc15', '#3b82f6', '#10b981', '#ef4444'];
    return colors[id % colors.length];
}
