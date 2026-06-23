import sys
import pandas as pd
import pymysql
import json
from datetime import datetime

def process_import(file_path):
    try:
        # Conexão com o banco de dados
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='lotofacil_db',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # 1. Obter último concurso
            cursor.execute("SELECT MAX(concurso) as max_concurso FROM concursos")
            result = cursor.fetchone()
            ultimo_concurso = result['max_concurso'] if result['max_concurso'] else 0

            # 2. Ler o Excel
            # A planilha da Caixa muitas vezes tem linhas em branco no início ou rodapé.
            # Vamos ler e encontrar a linha de cabeçalho.
            df = pd.read_excel(file_path)
            
            # Limpeza básica: procurar a coluna Concurso
            # Se a coluna 'Concurso' não estiver no cabeçalho, pode estar em uma das primeiras linhas
            if 'Concurso' not in df.columns:
                # Procura a linha que contém 'Concurso'
                header_row = None
                for i, row in df.iterrows():
                    if 'Concurso' in str(row.values):
                        header_row = i
                        break
                
                if header_row is not None:
                    df = pd.read_excel(file_path, header=header_row + 1)
            
            # Padroniza nomes das colunas
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Encontrar as colunas relevantes. A Caixa geralmente usa 'concurso', 'data sorteio', 'bola1', 'bola2' etc.
            # Vamos tentar inferir.
            concurso_col = next((c for c in df.columns if 'concurso' in c), 'concurso')
            data_col = next((c for c in df.columns if 'data' in c), 'data sorteio')
            
            # Remove linhas onde concurso é NaN
            df = df.dropna(subset=[concurso_col])
            
            # Filtra os novos concursos
            df = df[df[concurso_col] > ultimo_concurso]
            
            if df.empty:
                return json.dumps({"status": "success", "inserted": 0})

            # Pegar as dezenas do último concurso para calcular repetidas
            ultimo_sorteio_dezenas = set()
            if ultimo_concurso > 0:
                cursor.execute("SELECT b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15 FROM concursos WHERE concurso = %s", (ultimo_concurso,))
                res = cursor.fetchone()
                if res:
                    ultimo_sorteio_dezenas = set(res.values())

            primos_base = {2, 3, 5, 7, 11, 13, 17, 19, 23}
            inseridos = 0

            # Prepara as queries
            sql_concurso = """
                INSERT INTO concursos (concurso, data_sorteio, b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            sql_estatistica = """
                INSERT INTO estatisticas_concurso (concurso_id, qtd_pares, qtd_impares, qtd_primos, soma_dezenas, repetidas_anterior)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            for index, row in df.iterrows():
                try:
                    concurso_atual = int(row[concurso_col])
                    
                    # Tratar data
                    data_raw = row[data_col]
                    if isinstance(data_raw, pd.Timestamp) or isinstance(data_raw, datetime):
                        data_sorteio = data_raw.strftime('%Y-%m-%d')
                    else:
                        # Tentar converter string DD/MM/YYYY
                        try:
                            data_sorteio = datetime.strptime(str(data_raw).strip(), '%d/%m/%Y').strftime('%Y-%m-%d')
                        except:
                            data_sorteio = data_raw # Tenta jogar direto
                            
                    # Encontrar as 15 bolas
                    # Podem ser colunas com 'bola' no nome, ou apenas colunas subsequentes
                    bolas = []
                    for c in df.columns:
                        if 'bola' in c or 'dezena' in c:
                            bolas.append(int(row[c]))
                    
                    # Se não encontrou pelo nome, assume as primeiras 15 colunas numéricas após a data
                    if len(bolas) < 15:
                        # Tenta pegar todas as colunas que são numéricas e ver se temos as 15
                        # Isso é um fallback caso as colunas estejam nomeadas de forma estranha
                        pass
                        
                    if len(bolas) < 15:
                        continue # Pula se não achou as 15 dezenas
                        
                    bolas = bolas[:15] # Garante que são 15
                    bolas.sort() # Lotofácil dezenas vêm ordenadas na planilha geralmente, mas garantimos

                    # Inserir concurso
                    params_conc = [concurso_atual, data_sorteio] + bolas
                    cursor.execute(sql_concurso, params_conc)
                    
                    # Calcular estatísticas
                    pares = sum(1 for b in bolas if b % 2 == 0)
                    impares = 15 - pares
                    primos = sum(1 for b in bolas if b in primos_base)
                    soma = sum(bolas)
                    
                    repetidas = len(set(bolas).intersection(ultimo_sorteio_dezenas)) if ultimo_sorteio_dezenas else None
                    
                    # Inserir estatística
                    cursor.execute(sql_estatistica, (concurso_atual, pares, impares, primos, soma, repetidas))
                    
                    # Atualiza último concurso para a próxima iteração
                    ultimo_sorteio_dezenas = set(bolas)
                    inseridos += 1
                except Exception as e:
                    print(f"Erro na linha {index}: {e}", file=sys.stderr)
                    continue

        connection.commit()
        return json.dumps({"status": "success", "inserted": inseridos})

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Nenhum arquivo fornecido."}))
        sys.exit(1)
        
    arquivo_xlsx = sys.argv[1]
    resultado = process_import(arquivo_xlsx)
    print(resultado)
