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
    
    // Fetch initial data
    fetchData(periodFilter.value);

    // Event Listener for filter change
    periodFilter.addEventListener('change', (e) => {
        fetchData(e.target.value);
    });
});

async function fetchData(limit) {
    showLoader();
    try {
        const response = await fetch(`api/stats.php?limit=${limit}`);
        const data = await response.json();
        
        if (data.error) {
            alert('Erro ao carregar dados: ' + data.error);
            hideLoader();
            return;
        }

        updateTopCards(data.ultimo_concurso);
        updateFreqChart(data.frequencia);
        updateSomaChart(data.tendencia_somas);
        updatePIChart(data.padroes_pares_impares);
        updateRankings(data.frequencia, data.atraso);

    } catch (error) {
        console.error("Erro na requisição:", error);
        alert('Falha na comunicação com o servidor.');
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

    // Create Gradient
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
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
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
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { 
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    // Ideal Lotofacil sum range is ~180-210, so min 150 max 250 looks good
                    min: 140, max: 250 
                },
                x: { grid: { display: false }, ticks: { display: false } }
            },
            plugins: {
                legend: { display: false },
                annotation: {
                    // We could use chartjs-plugin-annotation here, but for simplicity we rely on grid
                }
            }
        }
    });
}

function updatePIChart(pi) {
    const ctx = document.getElementById('piChart').getContext('2d');
    
    if (piChartInstance) piChartInstance.destroy();

    // Get top 5 patterns
    const labels = pi.labels.slice(0, 5);
    const data = pi.data.slice(0, 5);

    piChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#facc15', '#a855f7', '#fbbf24', '#c084fc', '#fef08a'
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right' }
            },
            cutout: '70%'
        }
    });
}

function updateRankings(frequencia, atrasos) {
    // Quentes (Top 5 mais frequentes)
    const quentesList = document.getElementById('quentesList');
    quentesList.innerHTML = '';
    
    // Find the max frequency to calculate percentage
    const maxFreq = Math.max(...frequencia.data);

    for (let i = 0; i < 5; i++) {
        if (!frequencia.labels[i]) break;
        const dezena = frequencia.labels[i].toString().padStart(2, '0');
        const count = frequencia.data[i];
        const pct = (count / maxFreq) * 100;

        quentesList.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span class="rank-badge" style="color: #facc15;">${dezena}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">${count} vezes</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background: #facc15;"></div>
                </div>
            </li>
        `;
    }

    // Frias (Top 5 mais atrasadas)
    const friasList = document.getElementById('friasList');
    friasList.innerHTML = '';

    const maxAtraso = Math.max(...atrasos.data);

    for (let i = 0; i < 5; i++) {
        if (!atrasos.labels[i]) break;
        const dezena = atrasos.labels[i].toString().padStart(2, '0');
        const count = atrasos.data[i];
        const pct = maxAtraso > 0 ? (count / maxAtraso) * 100 : 0;

        // Se count for zero, não está atrasada. Mostrar pelo menos as 5 mais atrasadas.
        if (count === 0 && i > 0) continue; 

        friasList.innerHTML += `
            <li class="ranking-item">
                <div style="display:flex; align-items:center; gap: 10px;">
                    <span class="rank-badge" style="color: #06b6d4;">${dezena}</span>
                    <span style="font-size: 0.9rem; color: var(--text-muted);">${count} conc.</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" style="width: ${pct}%; background: #06b6d4;"></div>
                </div>
            </li>
        `;
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
