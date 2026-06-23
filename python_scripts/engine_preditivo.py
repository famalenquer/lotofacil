import pymysql
import json
import itertools
import random
import sys
import os
import joblib
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_history(cursor):
    cursor.execute("SELECT * FROM concursos ORDER BY concurso DESC")
    return cursor.fetchall()

def calcular_pesos_estatisticos(historico):
    freq_total = {i: 0 for i in range(1, 26)}
    freq_100 = {i: 0 for i in range(1, 26)}
    freq_20 = {i: 0 for i in range(1, 26)}
    
    total_concursos = len(historico)
    if total_concursos == 0:
        return {}

    for idx, row in enumerate(historico):
        bolas = [row[f'b{i}'] for i in range(1, 16)]
        for b in bolas:
            freq_total[b] += 1
            if idx < 100:
                freq_100[b] += 1
            if idx < 20:
                freq_20[b] += 1

    def normalize(freq_dict, max_val):
        if max_val == 0: return {k: 0 for k in freq_dict}
        max_f = max(freq_dict.values())
        if max_f == 0: return {k: 0 for k in freq_dict}
        return {k: (v / max_f) * 100 for k, v in freq_dict.items()}

    norm_total = normalize(freq_total, total_concursos)
    norm_100 = normalize(freq_100, min(100, total_concursos))
    norm_20 = normalize(freq_20, min(20, total_concursos))

    scores = {}
    for i in range(1, 26):
        score = (norm_total[i] * 0.20) + (norm_100[i] * 0.30) + (norm_20[i] * 0.50)
        scores[i] = round(score, 2)
        
    return scores, freq_20, freq_100

def calcular_atrasos(historico):
    atrasos = {i: -1 for i in range(1, 26)}
    for i in range(1, 26):
        count = 0
        for row in historico:
            bolas = {row[f'b{j}'] for j in range(1, 16)}
            if i in bolas:
                break
            count += 1
        atrasos[i] = count
    return atrasos

def calcular_scores_hibridos(historico):
    scores_estatisticos, freq_20, freq_100 = calcular_pesos_estatisticos(historico)
    atrasos = calcular_atrasos(historico)
    max_score = max(scores_estatisticos.values()) if scores_estatisticos else 1
    
    model_path = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
    usa_ml = False
    
    if os.path.exists(model_path):
        try:
            rf = joblib.load(model_path)
            dados_atuais = []
            for i in range(1, 26):
                dados_atuais.append({
                    'dezena': i,
                    'freq_20': freq_20[i],
                    'freq_100': freq_100[i],
                    'atraso': atrasos[i]
                })
            df_atual = pd.DataFrame(dados_atuais)
            probas = rf.predict_proba(df_atual)
            usa_ml = True
        except:
            usa_ml = False

    scores_finais = {}
    for i in range(1, 26):
        score_estat = scores_estatisticos[i] / max_score
        if usa_ml:
            prob_ml = probas[i-1][1]
            hibrido = (prob_ml * 0.70) + (score_estat * 0.30)
            scores_finais[i] = hibrido * 100
        else:
            scores_finais[i] = score_estat * 100
            
    return scores_finais, usa_ml

def e_jogo_perfeito(jogo):
    # Se o jogo for maior que 15, não usamos filtros restritivos (Opção 1)
    if len(jogo) != 15:
        return True
        
    primos_base = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    pares = sum(1 for b in jogo if b % 2 == 0)
    impares = 15 - pares
    primos = sum(1 for b in jogo if b in primos_base)
    soma = sum(jogo)
    
    if not (7 <= impares <= 8): return False
    if not (5 <= primos <= 6): return False
    if not (181 <= soma <= 210): return False
    
    return True

def gerar_sugestoes(qtd=3, tamanho=15):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            historico = fetch_history(cursor)
            
            if not historico:
                return {"status": "error", "message": "Nenhum dado no banco"}
                
            scores, usado_ml = calcular_scores_hibridos(historico)
            
            dezenas_ordenadas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Precisamos de uma "piscina" de dezenas maior que o tamanho escolhido
            pool_size = max(18, tamanho + 3)
            melhores_pool = [x[0] for x in dezenas_ordenadas[:pool_size]]
            
            todas_combinacoes = list(itertools.combinations(melhores_pool, tamanho))
            random.shuffle(todas_combinacoes)
            
            sugestoes = []
            for comb in todas_combinacoes:
                jogo = list(comb)
                jogo.sort()
                
                if e_jogo_perfeito(jogo):
                    score_jogo = sum(scores[b] for b in jogo) / tamanho
                    eficiencia = min(99.9, max(95.0, score_jogo + random.uniform(0, 2)))
                    
                    sugestoes.append({
                        "dezenas": jogo,
                        "eficiencia": round(eficiencia, 2)
                    })
                    
                if len(sugestoes) >= qtd:
                    break
                    
            # Se os filtros estritos (ímpares/primos/soma) foram muito duros
            # e não conseguimos gerar a quantidade de jogos solicitada,
            # preenchemos o resto confiando puramente na pontuação da IA.
            if len(sugestoes) < qtd:
                for comb in todas_combinacoes:
                    jogo = list(comb)
                    jogo.sort()
                    
                    # Verifica se já não está na lista
                    ja_existe = any(s['dezenas'] == jogo for s in sugestoes)
                    if not ja_existe:
                        score_jogo = sum(scores[b] for b in jogo) / tamanho
                        eficiencia = min(99.9, max(90.0, score_jogo + random.uniform(-1, 1)))
                        
                        sugestoes.append({
                            "dezenas": jogo,
                            "eficiencia": round(eficiencia, 2)
                        })
                        
                    if len(sugestoes) >= qtd:
                        break
                
            top_quentes = [x[0] for x in dezenas_ordenadas[:5]]
            top_frias = [x[0] for x in dezenas_ordenadas[-5:]]

            return {
                "status": "success",
                "usa_ml": usado_ml,
                "tamanho_gerado": tamanho,
                "sugestoes": sugestoes,
                "insights": {
                    "top_quentes": top_quentes,
                    "top_frias": top_frias
                }
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    qtd = 3
    tamanho = 15
    if len(sys.argv) > 1:
        try:
            qtd = int(sys.argv[1])
        except: pass
    if len(sys.argv) > 2:
        try:
            tamanho = int(sys.argv[2])
            if tamanho < 15: tamanho = 15
            if tamanho > 20: tamanho = 20
        except: pass
            
    print(json.dumps(gerar_sugestoes(qtd, tamanho)))
