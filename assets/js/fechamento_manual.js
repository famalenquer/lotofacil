let dezenasBase = [];
let dezenasFixas = [];
let regraAtual = {
    total: 18,
    fixas: 0
};

let ultimosJogosGerados = null;
let estrategiaNome = "";
let custoTotal = 0;

document.addEventListener("DOMContentLoaded", () => {
    renderVolante();
    atualizarRegras();
});

function renderVolante() {
    const container = document.getElementById("volanteInterativo");
    container.innerHTML = "";
    
    for (let i = 1; i <= 25; i++) {
        const btn = document.createElement("div");
        btn.className = "dezena-seletor";
        btn.innerText = i.toString().padStart(2, '0');
        btn.dataset.num = i;
        btn.onclick = () => toggleDezena(i);
        container.appendChild(btn);
    }
}

function atualizarRegras() {
    const strategy = document.getElementById("strategySelect").value;
    
    if (strategy === "normal" || strategy === "economico") {
        regraAtual.total = 18;
        regraAtual.fixas = 0;
        document.getElementById("legendaFixa").style.display = "none";
    } else if (strategy === "diamante_economico") {
        regraAtual.total = 19;
        regraAtual.fixas = 3;
        document.getElementById("legendaFixa").style.display = "flex";
    } else if (strategy === "diamante_supremo") {
        regraAtual.total = 20;
        regraAtual.fixas = 3;
        document.getElementById("legendaFixa").style.display = "flex";
    }
    
    // Check if the current selection exceeds new rules
    if (dezenasFixas.length > regraAtual.fixas) {
        // downgrade excess fixas to base
        while(dezenasFixas.length > regraAtual.fixas) {
            let removed = dezenasFixas.pop();
            if (!dezenasBase.includes(removed)) {
                dezenasBase.push(removed);
            }
        }
    }
    
    let totalSelecionado = dezenasBase.length + dezenasFixas.length;
    if (totalSelecionado > regraAtual.total) {
        // downgrade excess base
        while (dezenasBase.length + dezenasFixas.length > regraAtual.total) {
            dezenasBase.pop();
        }
    }
    
    atualizarUI();
}

function toggleDezena(num) {
    // Check if it's already a fixa
    if (dezenasFixas.includes(num)) {
        // Remove completely
        dezenasFixas = dezenasFixas.filter(d => d !== num);
        atualizarUI();
        return;
    }
    
    // Check if it's already a base
    if (dezenasBase.includes(num)) {
        // Remove completely
        dezenasBase = dezenasBase.filter(d => d !== num);
        atualizarUI();
        return;
    }
    
    // Not selected yet. Try to add.
    let totalSelecionado = dezenasBase.length + dezenasFixas.length;
    
    if (totalSelecionado >= regraAtual.total) {
        alert(`Você já selecionou o máximo de ${regraAtual.total} dezenas para esta estratégia.`);
        return;
    }
    
    // Prioritize fixas first
    if (dezenasFixas.length < regraAtual.fixas) {
        dezenasFixas.push(num);
    } else {
        dezenasBase.push(num);
    }
    
    atualizarUI();
}

function atualizarUI() {
    // Reset all buttons
    const btns = document.querySelectorAll('.dezena-seletor');
    btns.forEach(btn => {
        btn.classList.remove('selected-base', 'selected-fixa');
        const num = parseInt(btn.dataset.num);
        if (dezenasFixas.includes(num)) {
            btn.classList.add('selected-fixa');
        } else if (dezenasBase.includes(num)) {
            btn.classList.add('selected-base');
        }
    });
    
    // Update status text
    const statusEl = document.getElementById("statusSelecao");
    const btnGerar = document.getElementById("btnGerar");
    
    let varsNecessarias = regraAtual.total - regraAtual.fixas;
    
    let htmlStatus = "";
    let btnEnabled = true;
    
    if (dezenasFixas.length < regraAtual.fixas) {
        let faltam = regraAtual.fixas - dezenasFixas.length;
        htmlStatus += `<span style="color: #facc15">Selecione PRIMEIRO as suas FIXAS (Faltam ${faltam}).</span>`;
        btnEnabled = false;
    } else if (dezenasBase.length < varsNecessarias) {
        let faltam = varsNecessarias - dezenasBase.length;
        if (regraAtual.fixas > 0) {
            htmlStatus += `<span style="color: #60a5fa">Fixas OK! Agora selecione as VARIÁVEIS (Faltam ${faltam}).</span>`;
        } else {
            htmlStatus += `<span style="color: #60a5fa">Selecione as dezenas VARIÁVEIS (Faltam ${faltam}).</span>`;
        }
        btnEnabled = false;
    }
    
    if (btnEnabled) {
        htmlStatus = `<span style="color: #10b981; font-weight: bold;">✅ Todas as dezenas selecionadas! Pronto para gerar.</span>`;
    }
    
    statusEl.innerHTML = htmlStatus;
    btnGerar.disabled = !btnEnabled;
}

function limparVolante() {
    dezenasBase = [];
    dezenasFixas = [];
    atualizarUI();
    document.getElementById("resultados").style.display = "none";
}

async function gerarFechamentoManual() {
    const strategy = document.getElementById("strategySelect").value;
    
    // Combine to send to the backend
    let payload = {
        estrategia: strategy,
        dezenas_base: dezenasBase,
        dezenas_fixas: dezenasFixas
    };
    
    document.getElementById("loader").style.display = "block";
    setTimeout(() => { document.getElementById("loader").style.opacity = "1"; }, 10);
    document.getElementById("resultados").style.display = "none";
    
    try {
        const response = await fetch('api/run_fechamento_manual.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            mostrarResultados(data);
        } else {
            alert("Erro na otimização: " + data.message);
        }
    } catch (error) {
        console.error(error);
        alert("Erro de conexão ao gerar o fechamento.");
    } finally {
        document.getElementById("loader").style.opacity = "0";
        setTimeout(() => { document.getElementById("loader").style.display = "none"; }, 300);
    }
}

function mostrarResultados(data) {
    document.getElementById("resultados").style.display = "block";
    
    // Dezenas Base
    const divBase = document.getElementById("dezenasBase");
    divBase.innerHTML = '';
    
    // Show Fixas first, then base
    let todasSorted = [...data.dezenas_fixas, ...data.dezenas_base].sort((a,b) => a-b);
    
    todasSorted.forEach(d => {
        const span = document.createElement("span");
        span.className = "volante-bola";
        if (data.dezenas_fixas.includes(d)) {
            span.style.background = "linear-gradient(135deg, #facc15, #ca8a04)";
            span.style.color = "#1a1025";
            span.style.borderColor = "#fef08a";
        } else {
            span.style.background = "linear-gradient(135deg, #3b82f6, #2563eb)";
            span.style.color = "#fff";
            span.style.borderColor = "#60a5fa";
        }
        span.innerText = d.toString().padStart(2, '0');
        divBase.appendChild(span);
    });
    
    document.getElementById("qtdJogos").innerText = data.quantidade_jogos;
    let custo = data.quantidade_jogos * 3.50;
    document.getElementById("custoJogos").innerText = "R$ " + custo.toFixed(2).replace('.', ',');
    
    if (data.economia_reais) {
        document.getElementById("economiaJogos").innerText = "R$ " + data.economia_reais.toFixed(2).replace('.', ',');
    }
    
    custoTotal = custo;
    
    // Select name
    const select = document.getElementById("strategySelect");
    estrategiaNome = select.options[select.selectedIndex].text.split(':')[0].replace(/[^a-zA-ZÀ-ÿ0-9 ]/g, '').trim();
    
    // Render Jogos
    const grid = document.getElementById("volanteGrid");
    grid.innerHTML = '';
    
    ultimosJogosGerados = data.jogos;
    
    data.jogos.forEach((jogo, idx) => {
        const card = document.createElement("div");
        card.className = "volante-card";
        
        const title = document.createElement("div");
        title.style.color = "var(--primary)";
        title.style.fontWeight = "bold";
        title.style.marginBottom = "10px";
        title.innerText = "Jogo " + (idx + 1);
        card.appendChild(title);
        
        jogo.forEach(d => {
            const span = document.createElement("span");
            span.className = "volante-bola";
            if (data.dezenas_fixas.includes(d)) {
                span.style.background = "linear-gradient(135deg, #facc15, #ca8a04)";
                span.style.color = "#1a1025";
                span.style.borderColor = "#fef08a";
            }
            span.innerText = d.toString().padStart(2, '0');
            card.appendChild(span);
        });
        
        grid.appendChild(card);
    });
}

function exportarTXT() {
    if (!ultimosJogosGerados) return;
    
    let txt = "LotoFácil Pro - Fechamento Manual\n";
    txt += `Estratégia: ${estrategiaNome}\n`;
    txt += `Custo: R$ ${custoTotal.toFixed(2)}\n\n`;
    
    ultimosJogosGerados.forEach((jogo, idx) => {
        let jogoStr = jogo.map(n => n.toString().padStart(2, '0')).join(' ');
        txt += `Jogo ${idx+1}: ${jogoStr}\n`;
    });
    
    const blob = new Blob([txt], {type: "text/plain;charset=utf-8"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `lotofacil_manual_${new Date().getTime()}.txt`;
    link.click();
}

async function salvarJogo() {
    if (!ultimosJogosGerados) return;
    
    let todasAsDezenas = [...dezenasBase, ...dezenasFixas];
    
    const payload = {
        jogos: ultimosJogosGerados,
        custo: custoTotal,
        nome_estrategia: "Manual: " + estrategiaNome,
        dezenas_base: todasAsDezenas,
        dezenas_fixas: dezenasFixas
    };
    
    try {
        const response = await fetch('api/salvar_jogo.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            alert("✅ Jogo salvo com sucesso! Você pode acompanhá-lo na aba 'Meus Jogos'.");
            document.getElementById("btnSalvarJogo").disabled = true;
            document.getElementById("btnSalvarJogo").innerText = "✔️ Salvo";
        } else {
            alert("Erro ao salvar: " + result.message);
        }
    } catch (e) {
        alert("Erro de comunicação ao salvar jogo.");
    }
}
