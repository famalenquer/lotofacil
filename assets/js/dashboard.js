// assets/js/dashboard.js

// Global Chart Instances to allow destroying them on update
let freqChartInstance = null;
let somaChartInstance = null;
let piChartInstance = null;

// Chart.js Default Configs for Dark Mode
Chart.defaults.color = '#c4b5fd';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(26, 16, 37, 0.9)';
Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
Chart.defaults.plugins.tooltip.bodyColor = '#c4b5fd';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(250, 204, 21, 0.1)';
Chart.defaults.plugins.tooltip.borderWidth = 1;

document.addEventListener('DOMContentLoaded', () => {
    const periodFilter = document.getElementById('periodFilter');
    const cartelasFilter = document.getElementById('cartelasFilter');
    
    // Fetch initial data
    fetchData(periodFilter.value);
    if(cartelasFilter) fetchCartelas(cartelasFilter.value);

    // Event Listener for filter change
    periodFilter.addEventListener('change', (e) => {
        fetchData(e.target.value);
    });
    
    if(cartelasFilter) {
        cartelasFilter.addEventListener('change', (e) => {
            fetchCartelas(e.target.value);
        });
    }
});

async function fetchData(limit) {
    showLoader();
    try {
        const [resStats, resAi] = await Promise.all([
            fetch(`api/stats.php?limit=${limit}`),
            fetch(`api/dashboard_inteligente.php?limit=${limit}`)
        ]);
        
        const dataStats = await resStats.json();
        const dataAi = await resAi.json();
        
        if (dataStats.error) throw new Error(dataStats.error);
        if (dataAi.status === 'error') throw new Error(dataAi.message);

        updateTopCards(dataStats.ultimo_concurso);
        updateFreqChart(dataStats.frequencia);
        updateSomaChart(dataStats.tendencia_somas);
        updatePIChart(dataStats.padroes_pares_impares);
        
        renderHeatmap(dataAi.volante_calor);
        renderRaioX(dataAi.dezenas);
        updateRankingsInteligente(dataAi.quentes, dataAi.frias);

    } catch (error) {
        console.error("Erro na requisição:", error);
        alert('Falha na comunicação com o servidor: ' + error.message);
    }
    hideLoader();
}

function updateTopCards(ultimo) {
    document.getElementById('ultConcurso').innerText = ultimo.concurso;
    
    // Format Date
    const d = new Date(ultimo.data);
    document.getElementById('ultData').innerText = d.toLocaleDateString('pt-BR', {timeZone: 'UTC'});
    
    document.getElementById('ultSoma').innerText = ultimo.soma;
    document.getElementById('ultPI').innerText = `${ultimo.pares} / ${ultimo.impares}`;
    document.getElementById('ultPrimos').innerText = ultimo.primos;
    document.getElementById('ultRepetidas').innerText = ultimo.repetidas ?? '--';

    // Render Dezenas
    const container = document.getElementById('ultDezenas');
    container.innerHTML = '';
    ultimo.dezenas.forEach(d => {
        const el = document.createElement('div');
        el.className = 'dezena';
        el.innerText = d.toString().padStart(2, '0');
        container.appendChild(el);
    });
}

function updateFreqChart(frequencia) {
    const ctx = document.getElementById('freqChart').getContext('2d');
    if (freqChartInstance) freqChartInstance.destroy();
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(250, 204, 21, 0.8)');
    gradient.addColorStop(1, 'rgba(250, 204, 21, 0.1)');
    freqChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: frequencia.labels,
            datasets: [{
                label: 'Vezes Sorteada',
                data: frequencia.data,
                backgroundColor: gradient,
                borderColor: '#facc15',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updateSomaChart(somas) {
    const ctx = document.getElementById('somaChart').getContext('2d');
    if (somaChartInstance) somaChartInstance.destroy();
    somaChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: somas.labels,
            datasets: [{
                label: 'Soma',
                data: somas.data,
                borderColor: '#a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#a855f7',
                pointRadius: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, min: 140, max: 250 },
                x: { grid: { display: false }, ticks: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function updatePIChart(pi) {
    const ctx = document.getElementById('piChart').getContext('2d');
    if (piChartInstance) piChartInstance.destroy();
    const labels = pi.labels.slice(0, 5);
    const data = pi.data.slice(0, 5);
    piChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#facc15', '#a855f7', '#fbbf24', '#c084fc', '#fef08a'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } }, cutout: '70%' }
    });
}

function renderHeatmap(freq) {
    const container = document.getElementById('heatmapVolante');
    container.innerHTML = '';
    
    const freqs = Object.values(freq);
    const minFreq = Math.min(...freqs);
    const maxFreq = Math.max(...freqs);
    
    for (let i = 1; i <= 25; i++) {
        const f = freq[i] || 0;
        let p = 0;
        if (maxFreq > minFreq) {
            p = (f - minFreq) / (maxFreq - minFreq);
        } else {
            p = 0.5;
        }
        
        // Cor do mapa de calor (Azul = Frio, Amarelo/Laranja/Vermelho = Quente)
        // Hue vai de 220 (Azul) para 0 (Vermelho)
        const hue = (1 - p) * 220; 
        const corBg = `hsl(${hue}, 80%, 40%)`;
        
        const bola = document.createElement('div');
        bola.style.background = corBg;
        bola.style.color = '#fff';
        bola.style.borderRadius = '50%';
        bola.style.width = '50px';
        bola.style.height = '50px';
        bola.style.display = 'flex';
        bola.style.alignItems = 'center';
        bola.style.justifyContent = 'center';
        bola.style.fontWeight = 'bold';
        bola.style.fontSize = '1.1rem';
        bola.style.boxShadow = '0 2px 5px rgba(0,0,0,0.3)';
        bola.style.border = '2px solid rgba(255,255,255,0.1)';
        bola.title = `Saiu ${f} vezes neste recorte`;
        
        bola.innerText = i.toString().padStart(2, '0');
        container.appendChild(bola);
    }
}

function renderRaioX(dezenas) {
    const tbody = document.getElementById('raioxTabela');
    tbody.innerHTML = '';
    
    dezenas.forEach(d => {
        let color = '#fff';
        let statusBadge = '';
        
        if (d.status === 'Quente') {
            color = '#f87171';
            statusBadge = '<span style="background: rgba(248, 113, 113, 0.2); color: #f87171; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">🔥 Quente</span>';
        } else if (d.status === 'Fria') {
            color = '#60a5fa';
            statusBadge = '<span style="background: rgba(96, 165, 250, 0.2); color: #60a5fa; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">❄️ Fria</span>';
        } else {
            statusBadge = '<span style="background: rgba(255,255,255, 0.1); color: var(--text-muted); padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">Neutra</span>';
        }
        
        tbody.innerHTML += `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 10px; font-weight: bold; color: ${color};">${d.dezena.toString().padStart(2, '0')}</td>
                <td style="padding: 10px;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <span style="min-width: 45px;">${d.probabilidade}%</span>
                        <div style="width: 50px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                            <div style="width: ${d.probabilidade}%; height: 100%; background: ${color}; border-radius: 3px;"></div>
                        </div>
                    </div>
                </td>
                <td style="padding: 10px; color: var(--text-muted);">${d.atraso > 0 ? d.atraso : '-'}</td>
                <td style="padding: 10px;">${statusBadge}</td>
            </tr>
        `;
    });
}

function updateRankingsInteligente(quentes, frias) {
    const quentesList = document.getElementById('quentesList');
    quentesList.innerHTML = '';
    
    quentes.slice(0, 5).forEach(d => {
        quentesList.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span class="rank-badge" style="color: #facc15;">${d.dezena.toString().padStart(2, '0')}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">Prob. ${d.prob}%</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${d.prob}%; background: linear-gradient(90deg, #facc15, #ef4444);"></div>
                </div>
            </li>
        `;
    });

    const friasList = document.getElementById('friasList');
    friasList.innerHTML = '';

    frias.slice(0, 5).forEach(d => {
        friasList.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span class="rank-badge" style="color: #06b6d4;">${d.dezena.toString().padStart(2, '0')}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">${d.atraso} jogos sem sair</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: 100%; background: #06b6d4;"></div>
                </div>
            </li>
        `;
    });
    
    if (frias.length === 0) {
        friasList.innerHTML = '<li style="color: var(--text-muted); text-align: center; margin-top: 10px;">Nenhuma dezena muito atrasada</li>';
    }
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

async function fetchCartelas(limit) {
    try {
        const res = await fetch(`api/ultimos_jogos.php?limit=${limit}`);
        const data = await res.json();
        if (data.status === 'success') {
            renderCartelas(data.jogos);
        } else {
            console.error("Erro ao buscar cartelas:", data.error);
        }
    } catch (e) {
        console.error("Falha ao buscar cartelas", e);
    }
}

function renderCartelas(jogos) {
    const container = document.getElementById('cartelasContainer');
    if(!container) return;
    
    container.innerHTML = '';
    
    jogos.forEach(jogo => {
        const wrapper = document.createElement('div');
        wrapper.style.minWidth = '210px';
        wrapper.style.background = 'rgba(255, 255, 255, 0.03)';
        wrapper.style.padding = '15px';
        wrapper.style.borderRadius = '12px';
        wrapper.style.border = '1px solid rgba(255, 255, 255, 0.05)';
        wrapper.style.transition = 'transform 0.3s ease';
        wrapper.onmouseover = () => wrapper.style.transform = 'translateY(-3px)';
        wrapper.onmouseout = () => wrapper.style.transform = 'translateY(0)';
        
        const header = document.createElement('div');
        header.style.marginBottom = '15px';
        header.style.textAlign = 'center';
        
        const dataFormatada = new Date(jogo.data).toLocaleDateString('pt-BR', {timeZone: 'UTC'});
        header.innerHTML = `<div style="font-weight: 800; font-size: 1.1rem; color: var(--primary); letter-spacing: 0.5px;">Concurso ${jogo.concurso}</div>
                            <div style="font-size: 0.85rem; color: var(--text-muted);">${dataFormatada}</div>`;
                            
        wrapper.appendChild(header);
        
        const grid = document.createElement('div');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(5, 1fr)';
        grid.style.gap = '6px';
        
        for(let i = 1; i <= 25; i++) {
            const bola = document.createElement('div');
            bola.style.display = 'flex';
            bola.style.justifyContent = 'center';
            bola.style.alignItems = 'center';
            bola.style.width = '30px';
            bola.style.height = '30px';
            bola.style.borderRadius = '8px'; // Deixando levemente quadrado para o volante
            bola.style.fontSize = '0.9rem';
            bola.style.fontWeight = 'bold';
            bola.innerText = i.toString().padStart(2, '0');
            
            if (jogo.dezenas.includes(i)) {
                // Sorteada
                bola.style.background = 'linear-gradient(135deg, #a855f7, #7e22ce)';
                bola.style.color = '#fff';
                bola.style.boxShadow = '0 2px 8px rgba(168, 85, 247, 0.4)';
                bola.style.border = '1px solid rgba(255,255,255,0.2)';
            } else {
                // Não sorteada
                bola.style.background = 'rgba(0, 0, 0, 0.2)';
                bola.style.color = 'rgba(255, 255, 255, 0.2)';
                bola.style.border = '1px solid rgba(255,255,255,0.05)';
            }
            grid.appendChild(bola);
        }
        
        wrapper.appendChild(grid);
        container.appendChild(wrapper);
    });
}
