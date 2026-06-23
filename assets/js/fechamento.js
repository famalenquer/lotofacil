async function gerarFechamento() {
    showLoader();
    
    // Timeout forçado de 15 segundos para evitar que o navegador trave
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
        // Cache buster para evitar respostas corrompidas cacheadas
        const cacheBuster = new Date().getTime();
        const response = await fetch(`api/run_fechamento.php?t=${cacheBuster}`, {
            signal: controller.signal,
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        });
        
        clearTimeout(timeoutId);
        const text = await response.text();
        
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            console.error("Erro no Parse JSON. Resposta Bruta:", text);
            hideLoader();
            alert('Falha interna do servidor: A resposta não é um JSON válido. Verifique os logs.');
            return;
        }
        
        if (data.status === 'error') {
            hideLoader();
            alert('Erro reportado pelo Motor: ' + data.message);
            return;
        }

        renderResultados(data);
        hideLoader();
    } catch (error) {
        clearTimeout(timeoutId);
        console.error("Erro na requisição:", error);
        hideLoader();
        
        if (error.name === 'AbortError') {
            setTimeout(() => alert('Tempo Limite Esgotado! O servidor demorou mais de 15 segundos para responder. Tente novamente.'), 500);
        } else {
            setTimeout(() => alert('Falha grave na comunicação com o servidor. Tente atualizar a página.'), 500);
        }
    }
}

function renderResultados(data) {
    document.getElementById('resultados').style.display = 'block';
    
    // Render Dezenas Base
    const baseContainer = document.getElementById('dezenasBase');
    baseContainer.innerHTML = '';
    data.dezenas_base.forEach(num => {
        const el = document.createElement('div');
        el.className = 'dezena-base';
        el.innerText = num.toString().padStart(2, '0');
        baseContainer.appendChild(el);
    });
    
    // Render Dados Financeiros
    document.getElementById('qtdJogos').innerText = data.quantidade_jogos;
    
    const custo = data.quantidade_jogos * 3;
    document.getElementById('custoJogos').innerText = `R$ ${custo},00`;
    
    const econ = parseFloat(data.economia_reais).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    document.getElementById('economiaJogos').innerText = `R$ ${econ}`;
    
    // Render Volantes
    const grid = document.getElementById('volanteGrid');
    grid.innerHTML = '';
    
    data.jogos.forEach((jogo, idx) => {
        const card = document.createElement('div');
        card.className = 'volante-card';
        
        let bolas = '';
        jogo.forEach(num => {
            bolas += `<span class="volante-bola">${num.toString().padStart(2, '0')}</span>`;
        });
        
        card.innerHTML = `
            <div style="margin-bottom: 10px; font-weight:bold; color:var(--text-muted);">
                Bilhete ${idx + 1}
            </div>
            <div>${bolas}</div>
        `;
        grid.appendChild(card);
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
