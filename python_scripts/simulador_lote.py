import pymysql
import json
import sys

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def testar_lote_jogos(payload_json):
    try:
        dados = json.loads(payload_json)
        jogos = dados.get("jogos", [])
        
        if not jogos:
            return {"status": "error", "message": "Nenhum jogo fornecido"}
            
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM concursos ORDER BY concurso DESC")
            historico = cursor.fetchall()
            
        conn.close()
        
        if not historico:
            return {"status": "error", "message": "Banco vazio."}
            
        resultados_lote = []
        
        # Mapeamento do historico para sets
        historico_sets = []
        for row in historico:
            bolas = {row[f'b{i}'] for i in range(1, 16)}
            historico_sets.append({
                "concurso": row['concurso'],
                "dezenas": bolas
            })
            
        for idx, jogo in enumerate(jogos):
            meu_jogo_set = set(jogo)
            acertos_15 = 0
            acertos_14 = 0
            acertos_13 = 0
            
            for h in historico_sets:
                acertos = len(meu_jogo_set.intersection(h["dezenas"]))
                if acertos == 15: acertos_15 += 1
                elif acertos == 14: acertos_14 += 1
                elif acertos == 13: acertos_13 += 1
                
            resultados_lote.append({
                "index": idx,
                "acertos_15": acertos_15,
                "acertos_14": acertos_14,
                "acertos_13": acertos_13
            })
            
        return {
            "status": "success",
            "resultados": resultados_lote
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Ler JSON da entrada padrao (stdin)
    input_data = sys.stdin.read()
    print(json.dumps(testar_lote_jogos(input_data)))
