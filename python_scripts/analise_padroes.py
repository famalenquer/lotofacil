import pymysql
import json

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def analisar_padroes():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Puxa o histórico em ordem cronológica (ASC) para contar os ciclos corretamente
            cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
            historico_asc = cursor.fetchall()
            
            if not historico_asc:
                return {"status": "error", "message": "Nenhum dado no banco"}

            # MOLDURA E MIOLO
            moldura_base = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
            miolo_base = {7, 8, 9, 12, 13, 14, 17, 18, 19}
            
            # Variáveis para Ciclo
            ciclo_atual = 1
            dezenas_no_ciclo = set()
            concursos_no_ciclo_atual = 0
            
            historico_tamanho_ciclos = []
            
            # Análise do último concurso e histórico
            padroes_moldura = {}
            
            for row in historico_asc:
                bolas = {
                    row['b1'], row['b2'], row['b3'], row['b4'], row['b5'],
                    row['b6'], row['b7'], row['b8'], row['b9'], row['b10'],
                    row['b11'], row['b12'], row['b13'], row['b14'], row['b15']
                }
                
                # ------ Lógica de Ciclo ------
                dezenas_no_ciclo.update(bolas)
                concursos_no_ciclo_atual += 1
                
                if len(dezenas_no_ciclo) == 25:
                    # Ciclo fechou
                    historico_tamanho_ciclos.append(concursos_no_ciclo_atual)
                    ciclo_atual += 1
                    dezenas_no_ciclo = set()
                    concursos_no_ciclo_atual = 0
                
                # ------ Lógica de Moldura ------
                qtd_moldura = len(bolas.intersection(moldura_base))
                qtd_miolo = len(bolas.intersection(miolo_base))
                padrao_mol = f"{qtd_moldura}M/{qtd_miolo}C"
                
                if padrao_mol not in padroes_moldura:
                    padroes_moldura[padrao_mol] = 0
                padroes_moldura[padrao_mol] += 1
                
            # Dados do Ciclo Atual
            dezenas_faltantes = list(set(range(1, 26)) - dezenas_no_ciclo)
            dezenas_faltantes.sort()
            
            tamanho_medio_ciclo = sum(historico_tamanho_ciclos) / len(historico_tamanho_ciclos) if historico_tamanho_ciclos else 0
            
            # Ordenar Padrões de Moldura para pegar os mais frequentes
            padroes_moldura_ordenados = sorted(padroes_moldura.items(), key=lambda x: x[1], reverse=True)
            top_padroes_moldura = padroes_moldura_ordenados[:5]
            
            # Obter os últimos 100 resultados para a Média de Moldura Recente
            historico_desc = list(reversed(historico_asc))[:100]
            moldura_recente_soma = 0
            for row in historico_desc:
                 bolas = {row[f'b{i}'] for i in range(1, 16)}
                 moldura_recente_soma += len(bolas.intersection(moldura_base))
                 
            media_moldura_100 = moldura_recente_soma / len(historico_desc) if historico_desc else 0

            return {
                "status": "success",
                "ciclo": {
                    "numero_ciclo_atual": ciclo_atual,
                    "concursos_rodados": concursos_no_ciclo_atual,
                    "dezenas_sorteadas": list(dezenas_no_ciclo),
                    "dezenas_faltantes": dezenas_faltantes,
                    "tamanho_medio_historico": round(tamanho_medio_ciclo, 1)
                },
                "moldura": {
                    "top_padroes": top_padroes_moldura,
                    "media_ultimos_100": round(media_moldura_100, 1)
                }
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    print(json.dumps(analisar_padroes()))
