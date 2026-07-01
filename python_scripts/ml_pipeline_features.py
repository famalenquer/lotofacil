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
        cursor.execute("DROP TABLE IF EXISTS ml_features;")
        cursor.execute("""
            CREATE TABLE ml_features (
                id INT AUTO_INCREMENT PRIMARY KEY,
                concurso INT,
                dezena INT,
                freq_20 INT,
                freq_50 INT,
                freq_100 INT,
                freq_200 INT,
                freq_total INT,
                atraso_norm FLOAT,
                momentum FLOAT,
                sazonalidade INT,
                target INT,
                UNIQUE KEY unique_concurso_dezena (concurso, dezena)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    conn.close()

def build_features():
    print("Iniciando Pipeline Avançado de Feature Engineering...")
    setup_table()
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT concurso, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, data_sorteio FROM concursos ORDER BY concurso ASC")
        historico = cursor.fetchall()
        
        if len(historico) < 201:
            print("Histórico insuficiente para criar janela de 200 sorteios.")
            return

        historico_dict = {}
        concursos_ordenados = []
        dias_semana_dict = {}
        
        for row in historico:
            c = row['concurso']
            concursos_ordenados.append(c)
            bolas = {row[f'b{i}'] for i in range(1, 16)}
            historico_dict[c] = bolas
            if row['data_sorteio']:
                dias_semana_dict[c] = row['data_sorteio'].weekday()
            else:
                dias_semana_dict[c] = -1

        batch_data = []
        
        print("Calculando features (isso pode levar alguns segundos)...")
        for i in range(200, len(concursos_ordenados)):
            concurso_alvo = concursos_ordenados[i]
            dezenas_alvo = historico_dict[concurso_alvo]
            sazonalidade = dias_semana_dict.get(concurso_alvo, -1)
            
            janela_20 = concursos_ordenados[i-20:i]
            janela_50 = concursos_ordenados[i-50:i]
            janela_100 = concursos_ordenados[i-100:i]
            janela_200 = concursos_ordenados[i-200:i]
            janela_total = concursos_ordenados[:i]
            
            f_20 = {d: 0 for d in range(1, 26)}
            f_50 = {d: 0 for d in range(1, 26)}
            f_100 = {d: 0 for d in range(1, 26)}
            f_200 = {d: 0 for d in range(1, 26)}
            f_total = {d: 0 for d in range(1, 26)}
            
            for c_past in janela_total:
                for d in historico_dict[c_past]:
                    f_total[d] += 1
                    
            for c_past in janela_200:
                for d in historico_dict[c_past]: f_200[d] += 1
            for c_past in janela_100:
                for d in historico_dict[c_past]: f_100[d] += 1
            for c_past in janela_50:
                for d in historico_dict[c_past]: f_50[d] += 1
            for c_past in janela_20:
                for d in historico_dict[c_past]: f_20[d] += 1
                    
            atraso_count = {d: 0 for d in range(1, 26)}
            for d in range(1, 26):
                atraso = 0
                for c_past in reversed(concursos_ordenados[:i]):
                    if d in historico_dict[c_past]:
                        break
                    atraso += 1
                atraso_count[d] = atraso
                
            max_atraso = max(atraso_count.values()) if atraso_count else 1
            if max_atraso == 0: max_atraso = 1

            for dezena in range(1, 26):
                target = 1 if dezena in dezenas_alvo else 0
                
                atraso_norm = atraso_count[dezena] / max_atraso
                
                # Momentum: f_20 relativa vs f_100 relativa
                f_20_rel = f_20[dezena] / 20.0
                f_100_rel = f_100[dezena] / 100.0
                momentum = f_20_rel - f_100_rel
                
                batch_data.append((
                    concurso_alvo, dezena, 
                    f_20[dezena], f_50[dezena], f_100[dezena], f_200[dezena], f_total[dezena],
                    atraso_norm, momentum, sazonalidade, target
                ))

            if len(batch_data) >= 5000:
                cursor.executemany(
                    "INSERT IGNORE INTO ml_features (concurso, dezena, freq_20, freq_50, freq_100, freq_200, freq_total, atraso_norm, momentum, sazonalidade, target) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    batch_data
                )
                batch_data = []

        if batch_data:
            cursor.executemany(
                "INSERT IGNORE INTO ml_features (concurso, dezena, freq_20, freq_50, freq_100, freq_200, freq_total, atraso_norm, momentum, sazonalidade, target) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                batch_data
            )

    conn.close()
    print("Pipeline Avançado de Features concluído com sucesso!")

if __name__ == "__main__":
    start = time.time()
    build_features()
    end = time.time()
    print(f"Tempo total: {round(end - start, 2)} segundos.")
