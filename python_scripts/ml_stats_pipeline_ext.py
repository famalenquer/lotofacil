import pymysql
import json

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def create_extended_stats_table():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('DROP TABLE IF EXISTS estatisticas_concurso_ext')
        cur.execute('''
            CREATE TABLE estatisticas_concurso_ext (
                id INT AUTO_INCREMENT PRIMARY KEY,
                concurso INT UNIQUE,
                faixa_baixa INT,
                faixa_media INT,
                faixa_alta INT,
                linha_1 INT,
                linha_2 INT,
                linha_3 INT,
                linha_4 INT,
                linha_5 INT,
                coluna_1 INT,
                coluna_2 INT,
                coluna_3 INT,
                coluna_4 INT,
                coluna_5 INT,
                seq_2 INT,
                seq_3 INT,
                gap_1 INT,
                gap_2_3 INT,
                gap_4_plus INT,
                repet_n1 INT,
                repet_n2 INT,
                repet_n3 INT,
                soma_pares INT,
                soma_impares INT,
                soma_primos INT,
                data_sorteio DATE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
    conn.close()

def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    p = 3
    while p * p <= n:
        if n % p == 0:
            return False
        p += 2
    return True

PRIME_SET = {i for i in range(1, 26) if is_prime(i)}

def compute_stats(row):
    dezenas = [row[f'b{i}'] for i in range(1, 16)]
    baixa = sum(1 for d in dezenas if 1 <= d <= 8)
    media = sum(1 for d in dezenas if 9 <= d <= 17)
    alta = sum(1 for d in dezenas if 18 <= d <= 25)
    linha_1 = sum(1 for d in dezenas if 1 <= d <= 5)
    linha_2 = sum(1 for d in dezenas if 6 <= d <= 10)
    linha_3 = sum(1 for d in dezenas if 11 <= d <= 15)
    linha_4 = sum(1 for d in dezenas if 16 <= d <= 20)
    linha_5 = sum(1 for d in dezenas if 21 <= d <= 25)
    coluna_1 = sum(1 for d in dezenas if d % 5 == 1 or d % 5 == 0)
    coluna_2 = sum(1 for d in dezenas if d % 5 == 2)
    coluna_3 = sum(1 for d in dezenas if d % 5 == 3)
    coluna_4 = sum(1 for d in dezenas if d % 5 == 4)
    coluna_5 = sum(1 for d in dezenas if d % 5 == 0)  # numbers ending with 5
    # sequences
    s = sorted(dezenas)
    seq_2 = seq_3 = 0
    i = 0
    while i < len(s) - 1:
        if s[i+1] - s[i] == 1:
            seq_2 += 1
            if i < len(s) - 2 and s[i+2] - s[i+1] == 1:
                seq_3 += 1
                i += 2
            else:
                i += 1
        else:
            i += 1
    gaps = [s[i+1] - s[i] for i in range(len(s)-1)]
    gap_1 = sum(1 for g in gaps if g == 1)
    gap_2_3 = sum(1 for g in gaps if 2 <= g <= 3)
    gap_4_plus = sum(1 for g in gaps if g >= 4)
    soma_pares = sum(d for d in dezenas if d % 2 == 0)
    soma_impares = sum(d for d in dezenas if d % 2 != 0)
    soma_primos = sum(d for d in dezenas if d in PRIME_SET)
    return {
        'faixa_baixa': baixa,
        'faixa_media': media,
        'faixa_alta': alta,
        'linha_1': linha_1,
        'linha_2': linha_2,
        'linha_3': linha_3,
        'linha_4': linha_4,
        'linha_5': linha_5,
        'coluna_1': coluna_1,
        'coluna_2': coluna_2,
        'coluna_3': coluna_3,
        'coluna_4': coluna_4,
        'coluna_5': coluna_5,
        'seq_2': seq_2,
        'seq_3': seq_3,
        'gap_1': gap_1,
        'gap_2_3': gap_2_3,
        'gap_4_plus': gap_4_plus,
        'soma_pares': soma_pares,
        'soma_impares': soma_impares,
        'soma_primos': soma_primos,
        'data_sorteio': row.get('data_sorteio')
    }

def main():
    print('Running extended stats pipeline...')
    create_extended_stats_table()
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM concursos ORDER BY concurso ASC')
        concursos = cur.fetchall()
    # build sets for repetition counts
    sets = [{row[f'b{i}'] for i in range(1, 16)} for row in concursos]
    repetitions = {}
    for idx, row in enumerate(concursos):
        rep1 = len(sets[idx].intersection(sets[idx-1])) if idx > 0 else 0
        rep2 = len(sets[idx].intersection(sets[idx-2])) if idx > 1 else 0
        rep3 = len(sets[idx].intersection(sets[idx-3])) if idx > 2 else 0
        repetitions[row['concurso']] = (rep1, rep2, rep3)
    batch = []
    for row in concursos:
        stats = compute_stats(row)
        rep1, rep2, rep3 = repetitions.get(row['concurso'], (0,0,0))
        batch.append((
            row['concurso'], stats['faixa_baixa'], stats['faixa_media'], stats['faixa_alta'],
            stats['linha_1'], stats['linha_2'], stats['linha_3'], stats['linha_4'], stats['linha_5'],
            stats['coluna_1'], stats['coluna_2'], stats['coluna_3'], stats['coluna_4'], stats['coluna_5'],
            stats['seq_2'], stats['seq_3'],
            stats['gap_1'], stats['gap_2_3'], stats['gap_4_plus'],
            rep1, rep2, rep3,
            stats['soma_pares'], stats['soma_impares'], stats['soma_primos'],
            stats['data_sorteio']
        ))
        if len(batch) >= 2000:
            with conn.cursor() as cur:
                cur.executemany('''
                    INSERT INTO estatisticas_concurso_ext (
                        concurso, faixa_baixa, faixa_media, faixa_alta,
                        linha_1, linha_2, linha_3, linha_4, linha_5,
                        coluna_1, coluna_2, coluna_3, coluna_4, coluna_5,
                        seq_2, seq_3,
                        gap_1, gap_2_3, gap_4_plus,
                        repet_n1, repet_n2, repet_n3,
                        soma_pares, soma_impares, soma_primos,
                        data_sorteio
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                ''', batch)
            batch.clear()
    if batch:
        with conn.cursor() as cur:
            cur.executemany('''
                INSERT INTO estatisticas_concurso_ext (
                    concurso, faixa_baixa, faixa_media, faixa_alta,
                    linha_1, linha_2, linha_3, linha_4, linha_5,
                    coluna_1, coluna_2, coluna_3, coluna_4, coluna_5,
                    seq_2, seq_3,
                    gap_1, gap_2_3, gap_4_plus,
                    repet_n1, repet_n2, repet_n3,
                    soma_pares, soma_impares, soma_primos,
                    data_sorteio
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            ''', batch)
    conn.close()
    print('Extended stats pipeline completed.')

if __name__ == '__main__':
    main()
