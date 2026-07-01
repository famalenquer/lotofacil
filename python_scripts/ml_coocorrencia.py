import pymysql
import itertools

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def create_tables():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('DROP TABLE IF EXISTS estatisticas_duplas')
        cur.execute('''
            CREATE TABLE estatisticas_duplas (
                janela VARCHAR(20),
                dez_1 INT,
                dez_2 INT,
                ocorrencias_juntas INT,
                prob_condicional_1_dado_2 FLOAT,
                prob_condicional_2_dado_1 FLOAT,
                afinidade FLOAT,
                PRIMARY KEY (janela, dez_1, dez_2)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        
        cur.execute('DROP TABLE IF EXISTS estatisticas_triplas')
        cur.execute('''
            CREATE TABLE estatisticas_triplas (
                janela VARCHAR(20),
                dez_1 INT,
                dez_2 INT,
                dez_3 INT,
                ocorrencias_juntas INT,
                prob_condicional_k_dado_ij FLOAT,
                PRIMARY KEY (janela, dez_1, dez_2, dez_3)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
    conn.close()

def calcular_estatisticas(historico, janela_nome):
    N = len(historico)
    if N == 0: return [], []
    
    A = {i: 0 for i in range(1, 26)}
    C = {}
    T = {}
    
    for combo in itertools.combinations(range(1, 26), 2):
        C[combo] = 0
    for combo in itertools.combinations(range(1, 26), 3):
        T[combo] = 0

    for row in historico:
        bolas = sorted([row[f'b{j}'] for j in range(1, 16)])
        for b in bolas:
            A[b] += 1
            
        for combo in itertools.combinations(bolas, 2):
            C[combo] += 1
            
        for combo in itertools.combinations(bolas, 3):
            T[combo] += 1

    duplas_batch = []
    for combo in itertools.combinations(range(1, 26), 2):
        i, j = combo
        c_ij = C[combo]
        a_i = A[i]
        a_j = A[j]
        
        if a_i == 0 or a_j == 0: continue
            
        p_j_dado_i = c_ij / a_i
        p_i_dado_j = c_ij / a_j
        
        f_joint = c_ij / N
        p_i = a_i / N
        p_j = a_j / N
        
        f_esperado = p_i * p_j
        afinidade = f_joint / f_esperado if f_esperado > 0 else 0
        
        duplas_batch.append((
            janela_nome, i, j, c_ij, p_i_dado_j, p_j_dado_i, afinidade
        ))

    triplas_batch = []
    for combo in itertools.combinations(range(1, 26), 3):
        i, j, k = combo
        t_ijk = T[combo]
        
        if t_ijk > 0:
            c_ij = C[(i,j)]
            p_k_dado_ij = t_ijk / c_ij if c_ij > 0 else 0
            triplas_batch.append((janela_nome, i, j, k, t_ijk, p_k_dado_ij))
            
            c_ik = C[(i,k)]
            p_j_dado_ik = t_ijk / c_ik if c_ik > 0 else 0
            triplas_batch.append((janela_nome, i, k, j, t_ijk, p_j_dado_ik))
            
            c_jk = C[(j,k)]
            p_i_dado_jk = t_ijk / c_jk if c_jk > 0 else 0
            triplas_batch.append((janela_nome, j, k, i, t_ijk, p_i_dado_jk))

    return duplas_batch, triplas_batch

def main():
    print('Criando tabelas de Co-ocorrencia...')
    create_tables()
    
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM concursos ORDER BY concurso DESC")
        historico_total = cur.fetchall()
        
    print('Calculando estatisticas...')
    d_all, t_all = calcular_estatisticas(historico_total, 'all')
    d_200, t_200 = calcular_estatisticas(historico_total[:200], '200')
    d_100, t_100 = calcular_estatisticas(historico_total[:100], '100')
    d_50, t_50 = calcular_estatisticas(historico_total[:50], '50')
    d_30, t_30 = calcular_estatisticas(historico_total[:30], '30')
    d_20, t_20 = calcular_estatisticas(historico_total[:20], '20')
    d_10, t_10 = calcular_estatisticas(historico_total[:10], '10')
    
    duplas = d_all + d_200 + d_100 + d_50 + d_30 + d_20 + d_10
    triplas = t_all + t_200 + t_100 + t_50 + t_30 + t_20 + t_10
    
    print('Inserindo Duplas no banco...')
    with conn.cursor() as cur:
        cur.executemany('''
            INSERT INTO estatisticas_duplas 
            (janela, dez_1, dez_2, ocorrencias_juntas, prob_condicional_1_dado_2, prob_condicional_2_dado_1, afinidade) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', duplas)
        
    print('Inserindo Triplas no banco...')
    with conn.cursor() as cur:
        cur.executemany('''
            INSERT INTO estatisticas_triplas 
            (janela, dez_1, dez_2, dez_3, ocorrencias_juntas, prob_condicional_k_dado_ij) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', triplas)
        
    conn.close()
    print('Pipeline de Co-ocorrencia finalizado com sucesso!')

if __name__ == '__main__':
    main()
