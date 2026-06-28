-- Criação do banco de dados (se não existir)
CREATE DATABASE IF NOT EXISTS lotofacil_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lotofacil_db;

-- Tabela para armazenar os concursos brutos
CREATE TABLE IF NOT EXISTS concursos (
    concurso INT PRIMARY KEY,
    data_sorteio DATE NOT NULL,
    b1 TINYINT NOT NULL,
    b2 TINYINT NOT NULL,
    b3 TINYINT NOT NULL,
    b4 TINYINT NOT NULL,
    b5 TINYINT NOT NULL,
    b6 TINYINT NOT NULL,
    b7 TINYINT NOT NULL,
    b8 TINYINT NOT NULL,
    b9 TINYINT NOT NULL,
    b10 TINYINT NOT NULL,
    b11 TINYINT NOT NULL,
    b12 TINYINT NOT NULL,
    b13 TINYINT NOT NULL,
    b14 TINYINT NOT NULL,
    b15 TINYINT NOT NULL,
    -- Campos opcionais que a Caixa disponibiliza
    arrecadacao_total DECIMAL(15, 2) DEFAULT 0.00,
    ganhadores_15_acertos INT DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabela de cache para estatísticas de cada concurso
CREATE TABLE IF NOT EXISTS estatisticas_concurso (
    concurso_id INT PRIMARY KEY,
    qtd_pares TINYINT NOT NULL,
    qtd_impares TINYINT NOT NULL,
    qtd_primos TINYINT NOT NULL,
    soma_dezenas SMALLINT NOT NULL,
    repetidas_anterior TINYINT DEFAULT NULL, -- Pode ser null para o concurso 1
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (concurso_id) REFERENCES concursos(concurso) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabela para os jogos salvos do usuário
CREATE TABLE IF NOT EXISTS jogos_salvos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_estrategia VARCHAR(100) NOT NULL,
    dezenas_base JSON NOT NULL,
    dezenas_fixas JSON,
    jogos JSON NOT NULL,
    qtd_jogos INT NOT NULL,
    custo DECIMAL(10, 2) NOT NULL,
    concurso_alvo INT DEFAULT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
