import json
import sys
import pymysql
import engine_preditivo

def run_painel(limit):
    conn = engine_preditivo.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Pega o histórico completo (necessário para calcular atraso corretamente e z-score geral)
            historico = engine_preditivo.fetch_history(cursor)
    finally:
        conn.close()

    if not historico:
        return {"status": "error", "message": "Nenhum histórico encontrado"}
        
    # Limita o histórico para a análise de frequência (mapa de calor)
    historico_limitado = historico[:limit] if limit > 0 else historico
    
    # Frequência no período
    freq_periodo = {i: 0 for i in range(1, 26)}
    for row in historico_limitado:
        bolas = [row[f'b{j}'] for j in range(1, 16)]
        for b in bolas:
            freq_periodo[b] += 1
            
    # Atrasos absolutos (desde o último sorteio)
    atrasos = engine_preditivo.calcular_atrasos(historico)
    
    # Score híbrido (A IA do motor V7)
    # A função calcular_scores_hibridos já lê o historico completo, 
    # e dá pesos de curto/médio prazo.
    scores_hibridos, _ = engine_preditivo.calcular_scores_hibridos(historico)
    
    # Se a função retornar um dicionário para a base, nós vamos transformá-lo
    # Para o painel, o Score será mapeado de 0 a 100%. O valor retornado por
    # calcular_scores_hibridos já tem valores variados, precisamos normalizá-lo para %
    
    min_score = min(scores_hibridos.values())
    max_score = max(scores_hibridos.values())
    
    dezenas_info = []
    quentes = []
    frias = []
    
    for i in range(1, 26):
        # Normalizar para 0-100%
        if max_score > min_score:
            prob = ((scores_hibridos[i] - min_score) / (max_score - min_score)) * 100
        else:
            prob = 50.0
            
        prob = round(prob, 2)
        
        status = "Neutra"
        if prob >= 70:
            status = "Quente"
            quentes.append({"dezena": i, "prob": prob, "atraso": atrasos[i]})
        elif prob <= 35 or atrasos[i] > 4:
            status = "Fria"
            frias.append({"dezena": i, "prob": prob, "atraso": atrasos[i]})
            
        dezenas_info.append({
            "dezena": i,
            "frequencia_periodo": freq_periodo[i],
            "atraso": atrasos[i],
            "probabilidade": prob,
            "status": status,
            "score_bruto": scores_hibridos[i]
        })
        
    # Ordenar Quentes pela prob, Frias pelo atraso, Geral pela prob
    quentes = sorted(quentes, key=lambda x: x['prob'], reverse=True)
    frias = sorted(frias, key=lambda x: x['atraso'], reverse=True)
    dezenas_info = sorted(dezenas_info, key=lambda x: x['probabilidade'], reverse=True)

    return {
        "status": "success",
        "limit": limit,
        "dezenas": dezenas_info,
        "quentes": quentes,
        "frias": frias,
        "volante_calor": freq_periodo
    }

if __name__ == "__main__":
    limit = 100
    if len(sys.argv) > 1:
        try:
            limit_arg = sys.argv[1]
            if limit_arg == 'all':
                limit = 0
            else:
                limit = int(limit_arg)
        except:
            limit = 100
            
    print(json.dumps(run_painel(limit)))
