import pymysql
import json
import math

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def calcular_correlacao_e_alertas():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Pegar últimos 100 sorteios para uma amostra recente mais forte
            cursor.execute("SELECT * FROM concursos ORDER BY concurso DESC LIMIT 100")
            historico = cursor.fetchall()
            
            if not historico:
                return {"status": "error", "message": "Nenhum dado no banco"}

            n_concursos = len(historico)

            # Matriz de Co-ocorrência 25x25
            co_ocorrencia = {i: {j: 0 for j in range(1, 26)} for i in range(1, 26)}
            frequencia = {i: 0 for i in range(1, 26)}
            
            for row in historico:
                bolas = [row[f'b{i}'] for i in range(1, 16)]
                for b1 in bolas:
                    frequencia[b1] += 1
                    for b2 in bolas:
                        if b1 != b2:
                            co_ocorrencia[b1][b2] += 1
            
            # Formatar Melhores Parceiros por Dezena
            parcerias = {}
            for i in range(1, 26):
                # Ordena parceiros pelo numero de vezes que sairam juntos
                parceiros_ordenados = sorted(co_ocorrencia[i].items(), key=lambda x: x[1], reverse=True)
                top_3 = [x[0] for x in parceiros_ordenados[:3]]
                worst_3 = [x[0] for x in parceiros_ordenados[-3:]]
                parcerias[i] = {
                    "dezena": i,
                    "top_parceiros": top_3,
                    "piores_parceiros": worst_3
                }
            
            # Achar o Par mais forte de todos os 100 concursos
            pares_globais = {}
            for i in range(1, 26):
                for j in range(i+1, 26):
                    pares_globais[f"{i:02d} e {j:02d}"] = co_ocorrencia[i][j]
            
            top_pares_globais = sorted(pares_globais.items(), key=lambda x: x[1], reverse=True)[:5]

            # Alertas Estatísticos (Intervalo de Confiança)
            # A probabilidade teórica de uma dezena sair é de 15/25 = 0.60 (60%)
            prob_teorica = 0.60
            
            alertas = []
            
            # Calcula o desvio padrão de uma binomial n*p*(1-p)
            desvio_padrao = math.sqrt(n_concursos * prob_teorica * (1 - prob_teorica))
            
            media_esperada = n_concursos * prob_teorica # Em 100 concursos, o esperado é sair 60 vezes
            
            for i in range(1, 26):
                freq_real = frequencia[i]
                
                # Z-Score = (X - μ) / σ
                if desvio_padrao > 0:
                    z_score = (freq_real - media_esperada) / desvio_padrao
                else:
                    z_score = 0
                
                # Se Z-Score > 2 (muito acima do normal, anomalia quente)
                if z_score >= 1.96:
                    alertas.append({
                        "tipo": "quente",
                        "dezena": i,
                        "mensagem": f"Anomalia: A dezena {i} saiu {freq_real} vezes em {n_concursos} jogos. Isso está 2 desvios padrões ACIMA da média. Alta tendência de reversão (falha)."
                    })
                # Se Z-Score < -2 (muito abaixo do normal, anomalia fria)
                elif z_score <= -1.96:
                    alertas.append({
                        "tipo": "fria",
                        "dezena": i,
                        "mensagem": f"Anomalia: A dezena {i} saiu apenas {freq_real} vezes. Muito ABAIXO da média esperada ({media_esperada}). Alta probabilidade de começar a sair."
                    })

            return {
                "status": "success",
                "top_pares": top_pares_globais,
                "parcerias_detalhadas": parcerias,
                "alertas": alertas
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    print(json.dumps(calcular_correlacao_e_alertas()))
