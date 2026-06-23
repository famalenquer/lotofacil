# Lotofácil Pro Analytics 🎱

Uma plataforma profissional avançada para análise preditiva, inteligência estatística e backtesting de resultados da Lotofácil, desenvolvida com uma arquitetura híbrida focada em alta performance e cálculos matemáticos pesados.

---

## 🏗️ Arquitetura Tecnológica

O sistema foi desenhado separando responsabilidades para extrair o máximo de cada tecnologia:
- **Frontend & Roteamento (PHP + Vanilla JS/CSS)**: Responsável pela interface gráfica rica (Dark Mode / Glassmorphism), requisições assíncronas via AJAX e roteamento seguro. Utiliza a biblioteca `Chart.js` para renderização de gráficos complexos.
- **Armazenamento Estruturado (MySQL)**: Banco de dados relacional desenhado com alto nível de normalização para queries estatísticas. Possui uma tabela de "Cache" (`estatisticas_concurso`) para entregar respostas imediatas ao Dashboard sem precisar recalcular todo o histórico a cada F5.
- **Motor Preditivo e Processamento de Dados (Python)**: O "Cérebro" do sistema. Utiliza `pandas`, `pymysql` e bibliotecas matemáticas nativas para ingerir planilhas Excel massivas e gerar cálculos combinatórios complexos para a Inteligência Artificial.

---

## 🧩 Módulos e Funcionalidades

### 1. Hub Central (Menu Principal)
A porta de entrada do sistema. Um menu em grid moderno e interativo que unifica o acesso a todas as ferramentas da plataforma.

### 2. Módulo de Importação Inteligente (Atualizador de Base)
Sistema desenhado para manter o banco de dados atualizado a partir das planilhas oficiais (`.xlsx`) da Caixa Econômica Federal.
- **Anti-Duplicidade Dinâmico**: O sistema lê o último concurso do banco e descarta automaticamente todas as linhas do Excel que já foram importadas.
- **Sanitização de Dados**: O motor Python busca automaticamente as colunas de "Concurso" e "Data" em qualquer posição da planilha, ignorando cabeçalhos sujos comuns nos arquivos da Caixa.
- **Pré-Cálculo de Cache**: No momento do upload, o sistema já calcula e grava a quantidade de números Pares, Ímpares, Primos e a Soma do concurso, otimizando todas as visualizações futuras.

### 3. Painel Estatístico (Dashboard)
O coração visual do sistema, permitindo visualizar o comportamento da loteria e planejar jogos manuais baseados na Lei dos Grandes Números.
- **Filtro Temporal Dinâmico**: Os gráficos mudam instantaneamente sem recarregar a página para mostrar recortes dos últimos 20, 50, 100 ou 500 sorteios.
- **Tendência de Reversão à Média (Gráfico de Soma)**: Um gráfico de linhas que ajuda a prever se o próximo sorteio terá "números mais altos" ou "mais baixos" avaliando se a soma atual está muito esticada acima de 210 ou abaixo de 180.
- **Radar de Padrões (Pares/Ímpares)**: Gráfico do tipo Donut que comprova a tese estatística do jogo equilibrado, ranqueando as formações mais comuns (ex: 8 Ímpares / 7 Pares).
- **Ranking Termômetro (Quentes e Frias)**:
  - **Dezenas Quentes**: As dezenas que mais estão saindo na "fase" atual (acompanhadas de barra de progresso percentual).
  - **Dezenas Frias (Atrasadas)**: Monitoramento exato de há quantos concursos uma dezena não é sorteada (fundamental para fechamentos).

### 4. Inteligência Artificial (Motor Preditivo)
Um módulo focado em gerar o "Jogo Perfeito" utilizando cruzamento de probabilidades estatísticas.
- **Média Móvel Ponderada**: O algoritmo não olha os números de forma plana. Ele atribui um "Peso/Score" para cada dezena baseado em três fases:
  - **20% de Peso**: Frequência no Histórico Geral (Base).
  - **30% de Peso**: Frequência nos últimos 100 sorteios (Tendência de Médio Prazo).
  - **50% de Peso**: Frequência nos últimos 20 sorteios (Momento/Ciclo atual).
- **Filtro de Descarte Matemático**: A IA gera milhares de combinações com as melhores dezenas pontuadas, mas descarta impiedosamente qualquer jogo que fuja do padrão campeão. O jogo só é sugerido se:
  - Tiver exatamente 7 ou 8 números ímpares.
  - Tiver entre 5 e 6 números primos.
  - A soma total ficar entre 181 e 210.

### 5. Simulador Dinâmico (Backtesting Histórico)
Antes de gastar dinheiro real, o sistema permite testar jogos contra o passado.
- **Volante Flexível**: Suporta jogos de 15 a 20 dezenas, de acordo com as novas regras da loteria.
- **Viagem no Tempo**: O algoritmo pega o jogo que você desenhou e confronta com o banco de dados dos mais de 3.000 sorteios que já ocorreram na história.
- **Auditoria de Prêmios**: O sistema emite um laudo informando detalhadamente quantas vezes aquele jogo exato já teria sido premiado nas faixas de 11, 12, 13, 14 e nos cobiçados 15 acertos.
- **Integração Front-to-Back**: Você pode clicar em um jogo gerado pela IA e transferi-lo automaticamente para o Volante do Simulador para testar seu desempenho histórico no mesmo segundo.

---

## 🎨 Design System e UX

Toda a interface foi construída seguindo diretrizes rigorosas de design moderno:
- **Glassmorphism**: Painéis translúcidos em camadas simulando vidro fosco.
- **Dark Mode Padrão**: Fundo em tons profundos de Roxo Escuro (`#1a1025`) para conforto visual e foco nos dados.
- **Acentos Dourados**: Paleta de cor principal baseada em Amarelo/Dourado (`#facc15`) e Roxo Vibrante (`#a855f7`), trazendo uma sensação de plataforma "Premium" e exclusiva.
- **Micro-interações**: Animações de `popIn` para o carregamento de dezenas e efeitos de transição/escala sutil no `hover` de botões e painéis gráficos.
