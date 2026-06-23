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

def testar_jogo(dezenas_jogadas):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM concursos ORDER BY concurso DESC")
            historico = cursor.fetchall()
            
            if not historico:
                return {"status": "error", "message": "Nenhum dado no banco"}
            
            resultados = {
                15: 0, 14: 0, 13: 0, 12: 0, 11: 0, 'outros': 0
            }
            
            set_jogadas = set(dezenas_jogadas)
            
            for row in historico:
                bolas_sorteadas = {
                    row['b1'], row['b2'], row['b3'], row['b4'], row['b5'],
                    row['b6'], row['b7'], row['b8'], row['b9'], row['b10'],
                    row['b11'], row['b12'], row['b13'], row['b14'], row['b15']
                }
                
                acertos = len(set_jogadas.intersection(bolas_sorteadas))
                
                if acertos >= 11:
                    resultados[acertos] += 1
                else:
                    resultados['outros'] += 1
                    
            return {
                "status": "success",
                "total_concursos": len(historico),
                "resultados": resultados
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            # Espera receber as dezenas separadas por virgula (ex: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
            dezenas_str = sys.argv[1]
            dezenas = [int(x.strip()) for x in dezenas_str.split(',') if x.strip().isdigit()]
            
            if len(dezenas) < 15 or len(dezenas) > 20:
                print(json.dumps({"status": "error", "message": "Jogo deve ter entre 15 e 20 dezenas."}))
            else:
                print(json.dumps(testar_jogo(dezenas)))
        except Exception as e:
             print(json.dumps({"status": "error", "message": "Formato inválido. Erro: " + str(e)}))
    else:
        print(json.dumps({"status": "error", "message": "Dezenas não fornecidas"}))
