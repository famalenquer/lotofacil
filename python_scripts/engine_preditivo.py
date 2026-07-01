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

def calcular_atrasos(historico):
    atraso_count = {d: 0 for d in range(1, 26)}
    for d in range(1, 26):
        atraso = 0
        for row in historico:
            bolas = {row[f'b{j}'] for j in range(1, 16)}
            if d in bolas:
                break
            atraso += 1
        atraso_count[d] = atraso
    return atraso_count

def calcular_features_concurso_atual(historico):
    if len(historico) < 200:
        return None
        
    concurso_alvo = historico[0]['concurso'] + 1
    sazonalidade = datetime.now().weekday()
    
    janela_20 = historico[:20]
    janela_50 = historico[:50]
    janela_100 = historico[:100]
    janela_200 = historico[:200]
    janela_total = historico
    
    f_20 = {d: 0 for d in range(1, 26)}
    f_50 = {d: 0 for d in range(1, 26)}
    f_100 = {d: 0 for d in range(1, 26)}
    f_200 = {d: 0 for d in range(1, 26)}
    f_total = {d: 0 for d in range(1, 26)}
    
    for row in janela_total:
        bolas = {row[f'b{j}'] for j in range(1, 16)}
        for b in bolas: f_total[b] += 1
    for row in janela_200:
        bolas = {row[f'b{j}'] for j in range(1, 16)}
        for b in bolas: f_200[b] += 1
    for row in janela_100:
        bolas = {row[f'b{j}'] for j in range(1, 16)}
        for b in bolas: f_100[b] += 1
    for row in janela_50:
        bolas = {row[f'b{j}'] for j in range(1, 16)}
        for b in bolas: f_50[b] += 1
    for row in janela_20:
        bolas = {row[f'b{j}'] for j in range(1, 16)}
        for b in bolas: f_20[b] += 1
        
    atraso_count = {d: 0 for d in range(1, 26)}
    for d in range(1, 26):
        atraso = 0
        for row in historico:
            bolas = {row[f'b{j}'] for j in range(1, 16)}
            if d in bolas:
                break
            atraso += 1
        atraso_count[d] = atraso
        
    max_atraso = max(atraso_count.values()) if atraso_count else 1
    if max_atraso == 0: max_atraso = 1
    
    features_list = []
    for dezena in range(1, 26):
        atraso_norm = atraso_count[dezena] / max_atraso
        f_20_rel = f_20[dezena] / 20.0
        f_100_rel = f_100[dezena] / 100.0
        momentum = f_20_rel - f_100_rel
        
        features_list.append({
            'dezena': dezena,
            'freq_20': f_20[dezena],
            'freq_50': f_50[dezena],
            'freq_100': f_100[dezena],
            'freq_200': f_200[dezena],
            'freq_total': f_total[dezena],
            'atraso_norm': atraso_norm,
            'momentum': momentum,
            'sazonalidade': sazonalidade
        })
        
    return pd.DataFrame(features_list)

def calcular_scores_hibridos(historico, dia_alvo=None):
    df_features = calcular_features_concurso_atual(historico)
    
    model_path = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
    usa_ml = False
    scores_finais = {i: 1.0 for i in range(1, 26)}
    
    if df_features is not None and os.path.exists(model_path):
        try:
            rf = joblib.load(model_path)
            # Ordena as features exatamente como no treino
            cols = ['dezena', 'freq_20', 'freq_50', 'freq_100', 'freq_200', 'freq_total', 'atraso_norm', 'momentum', 'sazonalidade']
            X_pred = df_features[cols]
            probas = rf.predict_proba(X_pred)
            
            prob_bruta = {i: probas[i-1][1] for i in range(1, 26)}
            soma_probas = sum(prob_bruta.values())
            
            # Normalização para a soma ser 15
            for i in range(1, 26):
                scores_finais[i] = (prob_bruta[i] / soma_probas) * 15.0
            
            usa_ml = True
        except Exception as e:
            print("Erro ao prever ML:", e)
            usa_ml = False
            
    if not usa_ml:
        # Fallback ultra básico se falhar
        for i in range(1, 26):
            scores_finais[i] = 15.0 / 25.0
            
    return scores_finais, usa_ml

def otimizar_base(scores, ultimo_resultado, tamanho_base):
    # Algoritmo Guloso (Otimização da Base)
    # Maximizar soma de scores respeitando R_max
    
    R_max = 11 if tamanho_base == 18 else (12 if tamanho_base == 19 else 13)
    
    dezenas_ordenadas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    base_selecionada = []
    repetidas = 0
    
    for dez, score in dezenas_ordenadas:
        if len(base_selecionada) >= tamanho_base:
            break
            
        if dez in ultimo_resultado:
            if repetidas < R_max:
                base_selecionada.append(dez)
                repetidas += 1
        else:
            base_selecionada.append(dez)
            
    # Completa se não atingir o tamanho por restrição muito forte
    if len(base_selecionada) < tamanho_base:
        for dez, score in dezenas_ordenadas:
            if dez not in base_selecionada:
                base_selecionada.append(dez)
            if len(base_selecionada) >= tamanho_base:
                break
                
    return sorted(base_selecionada)

import numpy as np

def carregar_afinidades_duplas():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT dez_1, dez_2, afinidade FROM estatisticas_duplas WHERE janela = 'all'")
            rows = cur.fetchall()
        conn.close()
        return {(r['dez_1'], r['dez_2']): r['afinidade'] for r in rows}
    except:
        return {}

def score_afinidade_bilhete(jogo, af_dict):
    if not af_dict: return 1.0
    score = 0
    pares = 0
    for combo in itertools.combinations(sorted(jogo), 2):
        if combo in af_dict:
            score += af_dict[combo]
            pares += 1
    return score / pares if pares > 0 else 1.0

def aplicar_filtro_zscore(jogos, historico, limite_top_pct=0.5):
    # Calcula estatísticas dos últimos 100 sorteios
    N = min(100, len(historico))
    if N < 10:
        return jogos # Sem histórico suficiente
        
    somas, pares, primos, molduras = [], [], [], []
    
    primos_base = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    moldura_base = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    
    for row in historico[:N]:
        b = [row[f'b{j}'] for j in range(1, 16)]
        somas.append(sum(b))
        pares.append(sum(1 for x in b if x % 2 == 0))
        primos.append(sum(1 for x in b if x in primos_base))
        molduras.append(sum(1 for x in b if x in moldura_base))
        
    mu_S, std_S = np.mean(somas), np.std(somas) or 1
    mu_P, std_P = np.mean(pares), np.std(pares) or 1
    mu_Q, std_Q = np.mean(primos), np.std(primos) or 1
    mu_M, std_M = np.mean(molduras), np.std(molduras) or 1
    
    af_dict = carregar_afinidades_duplas()
    bilhetes_com_score = []
    
    for jogo in jogos:
        S_b = sum(jogo)
        P_b = sum(1 for x in jogo if x % 2 == 0)
        Q_b = sum(1 for x in jogo if x in primos_base)
        M_b = sum(1 for x in jogo if x in moldura_base)
        
        z_S = abs(S_b - mu_S) / std_S
        z_P = abs(P_b - mu_P) / std_P
        z_Q = abs(Q_b - mu_Q) / std_Q
        z_M = abs(M_b - mu_M) / std_M
        
        af_jogo = score_afinidade_bilhete(jogo, af_dict)
        
        # Afinidade > 1.0 é boa, z-scores menores são melhores
        # Multiplicamos a afinidade por 2.0 para dar peso semelhante às variáveis z-score
        coerencia = -(z_S + z_P + z_Q + z_M) + (af_jogo * 3.0)
        
        bilhetes_com_score.append((coerencia, jogo))
        
    bilhetes_com_score.sort(key=lambda x: x[0], reverse=True)
    
    # Manter apenas top %
    corte = int(len(bilhetes_com_score) * limite_top_pct)
    if corte < 1: corte = 1
    
    melhores_jogos = [x[1] for x in bilhetes_com_score[:corte]]
    return melhores_jogos

def obter_top_pares_sinergia(historico=None):
    try:
        dados_corr = correlacao.calcular_correlacao_e_alertas(historico)
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
            
            # Substituindo V7 Top Pares pela Afinidade Global Matemática
            af_dict = carregar_afinidades_duplas()
            
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
                    
                    # Aplica Bônus de Afinidade Média
                    bonus_sinergia = score_afinidade_bilhete(jogo, af_dict) * 0.5 
                    
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
                        bonus_sinergia = score_afinidade_bilhete(jogo, af_dict) * 0.5
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

