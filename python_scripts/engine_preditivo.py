import pymysql
import json
import itertools
import random
import sys
import os
import joblib
import pandas as pd
import warnings
from datetime import datetime

# Integrações da V5 e V7
import ml_kmeans
import stats_historicas
import correlacao

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

def calcular_score_sazonal(historico, dia_alvo=None):
    if dia_alvo is None:
        dia_alvo = datetime.now().weekday()
        
    freq_dia = {i: 0 for i in range(1, 26)}
    count_dia = 0
    
    for row in historico:
        if row.get('data_sorteio'):
            if row['data_sorteio'].weekday() == dia_alvo:
                count_dia += 1
                bolas = [row[f'b{i}'] for i in range(1, 16)]
                for b in bolas:
                    freq_dia[b] += 1
                    
    scores_sazonais = {}
    for i in range(1, 26):
        if count_dia > 0:
            prob = freq_dia[i] / count_dia
            # Normalize around the theoretical mean (0.60)
            scores_sazonais[i] = (prob / 0.60)
        else:
            scores_sazonais[i] = 1.0 # Neutral if no data
            
    return scores_sazonais

def calcular_momentum(historico):
    historico_recente = historico[:25]
    freq_5 = {i: 0 for i in range(1, 26)}
    freq_25 = {i: 0 for i in range(1, 26)}
    
    for idx, row in enumerate(historico_recente):
        bolas = [row[f'b{i}'] for i in range(1, 16)]
        for b in bolas:
            freq_25[b] += 1
            if idx < 5:
                freq_5[b] += 1
                
    scores_momentum = {}
    for i in range(1, 26):
        esperado_5 = (freq_25[i] / 25) * 5 if freq_25[i] > 0 else 0
        real_5 = freq_5[i]
        diff = real_5 - esperado_5
        
        # Modifier: -1.0 to +1.0 roughly
        modifier = 1.0 + (diff * 0.10)
        scores_momentum[i] = max(0.5, min(1.5, modifier))
        
    return scores_momentum

def calcular_scores_hibridos(historico):
    scores_estatisticos, freq_20, freq_100 = calcular_pesos_estatisticos(historico)
    atrasos = calcular_atrasos(historico)
    max_score = max(scores_estatisticos.values()) if scores_estatisticos else 1
    
    # V7: Momentum and Seasonality
    scores_sazonais = calcular_score_sazonal(historico)
    scores_momentum = calcular_momentum(historico)
    
    # ----------------------------------------------------
    # V6: Captura dos Verdadeiros Atrasos (Risco de Quebra)
    # ----------------------------------------------------
    stats = stats_historicas.run_historico()
    risco_map = {}
    if stats.get('status') == 'success':
        for item in stats['atrasos']:
            risco_map[item['dezena']] = item['risco_quebra']
    
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
            base_score = hibrido * 100
        else:
            base_score = score_estat * 100
            
        # Aplica Sazonalidade e Momentum (V7)
        base_score = base_score * scores_sazonais[i] * scores_momentum[i]
            
        # V6: Super Multiplicador de Risco Extremo (+50%)
        if risco_map.get(i, False):
            base_score *= 1.50
            
        scores_finais[i] = base_score
            
    return scores_finais, usa_ml

def obter_top_pares_sinergia():
    try:
        dados_corr = correlacao.calcular_correlacao_e_alertas()
        if dados_corr.get('status') == 'success':
            return dados_corr.get('top_pares', [])
    except:
        pass
    return []

def avaliar_sinergia_jogo(jogo, top_pares):
    # Calcula quantos dos top_pares estão contidos no jogo
    bonus = 0
    for par_str, freq in top_pares:
        # par_str é algo como "01 e 02" ou "01-02", a implementação de correlacao retorna "01 e 02"
        partes = par_str.replace(' e ', '-').split('-')
        if len(partes) == 2:
            try:
                p1 = int(partes[0])
                p2 = int(partes[1])
                if p1 in jogo and p2 in jogo:
                    bonus += 1
            except:
                pass
    return bonus

def e_jogo_perfeito_dinamico(jogo, perfil_clima, ultimo_resultado=None):
    if len(jogo) != 15:
        return True
        
    if ultimo_resultado is not None:
        repetidas = len(set(jogo).intersection(ultimo_resultado))
        if not (8 <= repetidas <= 10):
            return False

    primos_base = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    pares = sum(1 for b in jogo if b % 2 == 0)
    impares = 15 - pares
    primos = sum(1 for b in jogo if b in primos_base)
    moldura_base = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    moldura = sum(1 for b in jogo if b in moldura_base)
    soma = sum(jogo)
    
    if not perfil_clima:
        if not (7 <= impares <= 8): return False
        if not (5 <= primos <= 6): return False
        if not (181 <= soma <= 210): return False
        return True

    margem_soma = 15
    margem_impares = 2
    margem_primos = 2
    margem_moldura = 2
    
    soma_alvo = perfil_clima['media_soma']
    impares_alvo = perfil_clima['media_impares']
    primos_alvo = perfil_clima['media_primos']
    moldura_alvo = perfil_clima['media_moldura']
    
    if not ((impares_alvo - margem_impares) <= impares <= (impares_alvo + margem_impares)): return False
    if not ((primos_alvo - margem_primos) <= primos <= (primos_alvo + margem_primos)): return False
    if not ((moldura_alvo - margem_moldura) <= moldura <= (moldura_alvo + margem_moldura)): return False
    if not ((soma_alvo - margem_soma) <= soma <= (soma_alvo + margem_soma)): return False
    
    return True

def gerar_sugestoes(qtd=3, tamanho=15):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            historico = fetch_history(cursor)
            if not historico:
                return {"status": "error", "message": "Nenhum dado no banco"}
                
            kmeans_data = ml_kmeans.run_kmeans()
            perfil = None
            clima_id = -1
            if kmeans_data.get('status') == 'success':
                clima_id = kmeans_data.get('clima_atual', -1)
                perfil = kmeans_data['perfis_clusters'].get(str(clima_id))
                
            ultimo_resultado = {historico[0][f'b{j}'] for j in range(1, 16)}
                
            scores, usado_ml = calcular_scores_hibridos(historico)
            
            # V7: Top Pares Sinergia
            top_pares = obter_top_pares_sinergia()
            
            dezenas_ordenadas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            pool_size = max(18, tamanho + 3)
            melhores_pool = [x[0] for x in dezenas_ordenadas[:pool_size]]
            
            todas_combinacoes = list(itertools.combinations(melhores_pool, tamanho))
            random.shuffle(todas_combinacoes)
            
            sugestoes = []
            for comb in todas_combinacoes:
                jogo = list(comb)
                jogo.sort()
                
                if e_jogo_perfeito_dinamico(jogo, perfil, ultimo_resultado):
                    score_jogo = sum(scores[b] for b in jogo) / tamanho
                    
                    # Aplica Bônus de Sinergia (V7)
                    bonus_sinergia = avaliar_sinergia_jogo(jogo, top_pares) * 0.5 
                    
                    eficiencia = min(99.9, max(95.0, score_jogo + bonus_sinergia + random.uniform(0, 1)))
                    
                    sugestoes.append({
                        "dezenas": jogo,
                        "eficiencia": round(eficiencia, 2)
                    })
                    
                if len(sugestoes) >= qtd:
                    break
                    
            if len(sugestoes) < qtd:
                for comb in todas_combinacoes:
                    jogo = list(comb)
                    jogo.sort()
                    ja_existe = any(s['dezenas'] == jogo for s in sugestoes)
                    if not ja_existe:
                        score_jogo = sum(scores[b] for b in jogo) / tamanho
                        bonus_sinergia = avaliar_sinergia_jogo(jogo, top_pares) * 0.5
                        eficiencia = min(99.9, max(90.0, score_jogo + bonus_sinergia + random.uniform(-1, 0.5)))
                        sugestoes.append({"dezenas": jogo, "eficiencia": round(eficiencia, 2)})
                    if len(sugestoes) >= qtd:
                        break
                
            top_quentes = [x[0] for x in dezenas_ordenadas[:5]]
            top_frias = [x[0] for x in dezenas_ordenadas[-5:]]

            return {
                "status": "success",
                "usa_ml": usado_ml,
                "tamanho_gerado": tamanho,
                "clima_usado": clima_id,
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

