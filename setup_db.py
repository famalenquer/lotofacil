import pymysql

try:
    # Conecta no MySQL sem especificar o banco de dados
    connection = pymysql.connect(host='localhost', user='root', password='')
    cursor = connection.cursor()

    # Cria o banco de dados
    print("Criando banco de dados...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS lotofacil_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    
    # Seleciona o banco
    cursor.execute("USE lotofacil_db")
    
    # Lê e executa o schema.sql
    print("Criando tabelas...")
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
        
    # Como pymysql não executa multiplos statements por padrão facilmente se a string tiver comentários soltos,
    # Vamos dividir ou executar os CREATE TABLE manualmente.
    
    # Criar Tabela concursos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS concursos (
        concurso INT PRIMARY KEY,
        data_sorteio DATE NOT NULL,
        b1 TINYINT NOT NULL, b2 TINYINT NOT NULL, b3 TINYINT NOT NULL,
        b4 TINYINT NOT NULL, b5 TINYINT NOT NULL, b6 TINYINT NOT NULL,
        b7 TINYINT NOT NULL, b8 TINYINT NOT NULL, b9 TINYINT NOT NULL,
        b10 TINYINT NOT NULL, b11 TINYINT NOT NULL, b12 TINYINT NOT NULL,
        b13 TINYINT NOT NULL, b14 TINYINT NOT NULL, b15 TINYINT NOT NULL,
        arrecadacao_total DECIMAL(15, 2) DEFAULT 0.00,
        ganhadores_15_acertos INT DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)

    # Criar Tabela estatisticas_concurso
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estatisticas_concurso (
        concurso_id INT PRIMARY KEY,
        qtd_pares TINYINT NOT NULL,
        qtd_impares TINYINT NOT NULL,
        qtd_primos TINYINT NOT NULL,
        soma_dezenas SMALLINT NOT NULL,
        repetidas_anterior TINYINT DEFAULT NULL,
        atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (concurso_id) REFERENCES concursos(concurso) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)

    # Criar Tabela jogos_salvos
    cursor.execute("""
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
    """)

    connection.commit()
    print("Banco de dados e tabelas criados com sucesso!")

except Exception as e:
    print(f"Erro: {e}")
finally:
    if 'connection' in locals() and connection.open:
        cursor.close()
        connection.close()
