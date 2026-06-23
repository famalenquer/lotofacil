import json
import itertools
import engine_preditivo

def intersecao(c1, c2):
    return len(set(c1).intersection(set(c2)))

def gerar_fechamento_18_15_14():
    """
    Fechamento de 18 dezenas escolhidas, jogando bilhetes de 15,
    com garantia de 14 pontos se as 15 sorteadas estiverem entre as 18.
    """
    try:
        conn = engine_preditivo.get_db_connection()
        with conn.cursor() as cursor:
            historico = engine_preditivo.fetch_history(cursor)
        conn.close()
        
        if not historico:
            return {"status": "error", "message": "Sem dados no banco."}
            
        scores, usa_ml = engine_preditivo.calcular_scores_hibridos(historico)
        dezenas_ordenadas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Pega as 18 melhores
        melhores_18 = sorted([x[0] for x in dezenas_ordenadas[:18]])
        
        # Mapeamento para acelerar a combinatória (Bitwise)
        idx_to_num = {i: melhores_18[i] for i in range(18)}
        universo_idx = list(itertools.combinations(range(18), 15))
        
        universo_masks = []
        for comb in universo_idx:
            mask = 0
            for bit in comb:
                mask |= (1 << bit)
            universo_masks.append(mask)
            
        alvos_nao_cobertos = set(universo_masks)
        bilhetes_escolhidos_masks = []
        
        # PRÉ-CÁLCULO (Faz o bit_count apenas 1 vez por par, gerando a matriz em C-Level)
        cobertura_dict = {}
        for c in universo_masks:
            cobertura_dict[c] = {alvo for alvo in alvos_nao_cobertos if (c & alvo).bit_count() >= 14}
        
        # Algoritmo Guloso (Set Cover) - Usando cache O(1)
        while alvos_nao_cobertos:
            melhor_bilhete = None
            max_cobertura = -1
            alvos_cobertos_pelo_melhor = set()
            
            for candidato in universo_masks:
                # Interseção nativa de sets em C (MUITO mais rápido que recalcular o bit_count no Python puro)
                cobertos = cobertura_dict[candidato] & alvos_nao_cobertos
                
                if len(cobertos) > max_cobertura:
                    max_cobertura = len(cobertos)
                    melhor_bilhete = candidato
                    alvos_cobertos_pelo_melhor = cobertos
                    
            bilhetes_escolhidos_masks.append(melhor_bilhete)
            alvos_nao_cobertos -= alvos_cobertos_pelo_melhor
            
        # Converter Masks de volta para dezenas reais
        jogos = []
        for mask in bilhetes_escolhidos_masks:
            jogo_real = []
            for i in range(18):
                if (mask & (1 << i)):
                    jogo_real.append(idx_to_num[i])
            jogos.append(jogo_real)
            
        return {
            "status": "success",
            "dezenas_base": melhores_18,
            "quantidade_jogos": len(jogos),
            "jogos": jogos,
            "economia_reais": (816 - len(jogos)) * 3.00, # Economia real baseada no preço da aposta simples (R$ 3,00)
            "usa_ml": usa_ml
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(json.dumps(gerar_fechamento_18_15_14()))
