document.addEventListener('DOMContentLoaded', () => {
    let chartLinhasInstance = null;
    let chartColunasInstance = null;
    function carregarEstatisticasAvançadas(limit) {
        fetch('api/estatisticas.php?limit=' + limit)
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    const m = data.medias;
                    document.getElementById('statDistBMA').innerText = m.faixa_baixa + ' / ' + m.faixa_media + ' / ' + m.faixa_alta;
                    document.getElementById('statSomas').innerText = 'P: ' + m.soma_pares + ' | Í: ' + m.soma_impares + ' | Pr: ' + m.soma_primos;
                    document.getElementById('statSeqs').innerText = 'Duplas: ' + m.seq_2 + ' | Triplas: ' + m.seq_3;
                    document.getElementById('statGap4').innerText = m.gap_4_plus;
                    document.getElementById('statRepeticoes').innerText = 'n-1: ' + m.repet_n1 + ' | n-2: ' + m.repet_n2;
                    renderizarGraficosMini(m);
                }
            });
    }
    function renderizarGraficosMini(m) {
        const ctxL = document.getElementById('chartLinhas').getContext('2d');
        const ctxC = document.getElementById('chartColunas').getContext('2d');
        if(chartLinhasInstance) chartLinhasInstance.destroy();
        if(chartColunasInstance) chartColunasInstance.destroy();
        const opt = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 5 } } };
        chartLinhasInstance = new Chart(ctxL, { type: 'bar', data: { labels: ['L1','L2','L3','L4','L5'], datasets: [{ data: [m.linha_1, m.linha_2, m.linha_3, m.linha_4, m.linha_5], backgroundColor: '#3b82f6' }] }, options: opt });
        chartColunasInstance = new Chart(ctxC, { type: 'bar', data: { labels: ['C1','C2','C3','C4','C5'], datasets: [{ data: [m.coluna_1, m.coluna_2, m.coluna_3, m.coluna_4, m.coluna_5], backgroundColor: '#ef4444' }] }, options: opt });
    }
    const sel = document.getElementById('periodFilter');
    carregarEstatisticasAvançadas(sel.value === 'all' ? 0 : parseInt(sel.value));
    sel.addEventListener('change', (e) => carregarEstatisticasAvançadas(e.target.value === 'all' ? 0 : parseInt(e.target.value)));
});