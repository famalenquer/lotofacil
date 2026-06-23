import pymysql
import json
import time

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def setup_table():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_features (
                id INT AUTO_INCREMENT PRIMARY KEY,
                concurso INT,
                dezena INT,
                freq_20 INT,
                freq_100 INT,
                atraso INT,
                target INT,
                UNIQUE KEY unique_concurso_dezena (concurso, dezena)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    conn.close()

def build_features():
    print("Iniciando Pipeline de Feature Engineering...")
    setup_table()
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Puxa histórico completo
        cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
        historico = cursor.fetchall()
        
        if len(historico) < 101:
            print("Histórico insuficiente para criar janela de 100 sorteios.")
            return

        # Para facilitar a busca, converte o histórico num dict de sets
        # concurso_dict[numero_concurso] = {dezenas...}
        historico_dict = {}
        concursos_ordenados = []
        for row in historico:
            c = row['concurso']
            concursos_ordenados.append(c)
            bolas = {row[f'b{i}'] for i in range(1, 16)}
            historico_dict[c] = bolas

        batch_data = []
        
        print("Calculando features (isso pode levar alguns segundos)...")
        # Começamos do concurso 101, pois precisamos de 100 passados para calcular features
        for i in range(100, len(concursos_ordenados)):
            concurso_alvo = concursos_ordenados[i]
            dezenas_alvo = historico_dict[concurso_alvo]
            
            # Pegamos os 100 anteriores
            janela_100 = concursos_ordenados[i-100:i]
            janela_20 = concursos_ordenados[i-20:i]
            
            # Conta frequencias
            freq_100_count = {d: 0 for d in range(1, 26)}
            freq_20_count = {d: 0 for d in range(1, 26)}
            
            for c_past in janela_100:
                for d in historico_dict[c_past]:
                    freq_100_count[d] += 1
                    
            for c_past in janela_20:
                for d in historico_dict[c_past]:
                    freq_20_count[d] += 1
                    
            # Atraso (última vez que saiu)
            atraso_count = {d: 0 for d in range(1, 26)}
            # Varre de trás para frente a partir de i-1
            for d in range(1, 26):
                atraso = 0
                for c_past in reversed(concursos_ordenados[:i]):
                    if d in historico_dict[c_past]:
                        break
                    atraso += 1
                atraso_count[d] = atraso

            # Constroi as linhas para as 25 dezenas
            for dezena in range(1, 26):
                target = 1 if dezena in dezenas_alvo else 0
                batch_data.append((
                    concurso_alvo, dezena, 
                    freq_20_count[dezena], freq_100_count[dezena], 
                    atraso_count[dezena], target
                ))

            # Salva em blocos de 500 sorteios para não estourar memória
            if len(batch_data) >= 5000:
                cursor.executemany(
                    "INSERT IGNORE INTO ml_features (concurso, dezena, freq_20, freq_100, atraso, target) VALUES (%s, %s, %s, %s, %s, %s)",
                    batch_data
                )
                batch_data = []

        # Restante
        if batch_data:
            cursor.executemany(
                "INSERT IGNORE INTO ml_features (concurso, dezena, freq_20, freq_100, atraso, target) VALUES (%s, %s, %s, %s, %s, %s)",
                batch_data
            )

    conn.close()
    print("Pipeline de Features concluído com sucesso!")

if __name__ == "__main__":
    start = time.time()
    build_features()
    end = time.time()
    print(f"Tempo total: {round(end - start, 2)} segundos.")
