document.addEventListener('DOMContentLoaded', () => {
    
    const selDezenaBase = document.getElementById('dezenaBaseSelect');
    const selTripla1 = document.getElementById('triplaBase1Select');
    const selTripla2 = document.getElementById('triplaBase2Select');
    const tbDuplas = document.getElementById('duplasTabela');
    const tbTriplas = document.getElementById('triplasTabela');
    const coocorrenciaFilter = document.getElementById('coocorrenciaFilter');

    // Populate selects 1 to 25
    for(let i=1; i<=25; i++) {
        let opt1 = document.createElement('option'); opt1.value = i; opt1.text = i.toString().padStart(2, '0');
        let opt2 = document.createElement('option'); opt2.value = i; opt2.text = i.toString().padStart(2, '0');
        let opt3 = document.createElement('option'); opt3.value = i; opt3.text = i.toString().padStart(2, '0');
        
        if (i === 1) opt1.selected = true;
        if (i === 1) opt2.selected = true;
        if (i === 2) opt3.selected = true; // Default 01 & 02

        selDezenaBase.appendChild(opt1);
        selTripla1.appendChild(opt2);
        selTripla2.appendChild(opt3);
    }

    function formatProb(prob) {
        return (prob * 100).toFixed(1) + '%';
    }

    function getJanela() {
        return coocorrenciaFilter.value; // Pode ser '10', '20', '30', '50', '100', 'all'
    }

    function carregarDuplas() {
        const dez = selDezenaBase.value;
        const janela = getJanela();
        
        fetch('api/duplas_triplas.php?tipo=dupla&dezena=' + dez + '&janela=' + janela)
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    tbDuplas.innerHTML = '';
                    if(data.parceiras.length === 0) {
                        tbDuplas.innerHTML = '<tr><td colspan="4">Sem dados</td></tr>';
                        return;
                    }
                    data.parceiras.forEach(row => {
                        let af = parseFloat(row.afinidade);
                        let color = af >= 1.1 ? '#10b981' : (af <= 0.9 ? '#ef4444' : '#a0aec0');
                        let tr = document.createElement('tr');
                        tr.innerHTML = '<td><span class="bola" style="display:inline-block; width:24px; height:24px; line-height:24px; font-size:0.8rem; padding:0; margin:0;">' + row.parceira.toString().padStart(2,'0') + '</span></td>' +
                                       '<td>' + formatProb(row.prob_condicional) + '</td>' +
                                       '<td>' + row.ocorrencias_juntas + 'x</td>' +
                                       '<td style="color:' + color + '; font-weight:bold;">' + af.toFixed(2) + '</td>';
                        tbDuplas.appendChild(tr);
                    });
                }
            })
            .catch(err => console.error(err));
    }

    function carregarTriplas() {
        const d1 = selTripla1.value;
        const d2 = selTripla2.value;
        const janela = getJanela();
        
        if(d1 === d2) {
            tbTriplas.innerHTML = '<tr><td colspan="3">Escolha dezenas diferentes</td></tr>';
            return;
        }

        fetch('api/duplas_triplas.php?tipo=tripla&dez1=' + d1 + '&dez2=' + d2 + '&janela=' + janela)
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    tbTriplas.innerHTML = '';
                    if(data.completam.length === 0) {
                        tbTriplas.innerHTML = '<tr><td colspan="3">Nenhum trio formado</td></tr>';
                        return;
                    }
                    data.completam.forEach(row => {
                        let tr = document.createElement('tr');
                        tr.innerHTML = '<td><span class="bola" style="display:inline-block; width:24px; height:24px; line-height:24px; font-size:0.8rem; padding:0; margin:0;">' + row.completa.toString().padStart(2,'0') + '</span></td>' +
                                       '<td>' + formatProb(row.prob_condicional) + '</td>' +
                                       '<td>' + row.ocorrencias_juntas + 'x</td>';
                        tbTriplas.appendChild(tr);
                    });
                }
            })
            .catch(err => console.error(err));
    }

    selDezenaBase.addEventListener('change', carregarDuplas);
    selTripla1.addEventListener('change', carregarTriplas);
    selTripla2.addEventListener('change', carregarTriplas);
    coocorrenciaFilter.addEventListener('change', () => {
        carregarDuplas();
        carregarTriplas();
    });

    // Initial load
    carregarDuplas();
    carregarTriplas();
});
