import json
import itertools
import sys
import engine_preditivo
import ml_kmeans

def intersecao(c1, c2):
    return len(set(c1).intersection(set(c2)))

def gerar_fechamento(estrategia='normal'):
    """
    Fechamento de 18 dezenas escolhidas, jogando bilhetes de 15.
    Estrategias:
    - normal: Garante 14 pontos se acertar 15 (Custo ~R$84)
    - economico: Garante 13 pontos se acertar 15 (Custo ~R$21)
    - filtro_ia: Garante 14 pontos, mas destrói jogos que fogem do K-Means (Custo Variável)
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
        
        # PRÉ-CÁLCULO: Define o Alvo de Acertos baseado na Estratégia
        acertos_alvo = 13 if estrategia == 'economico' else 14
        
        cobertura_dict = {}
        for c in universo_masks:
            cobertura_dict[c] = {alvo for alvo in alvos_nao_cobertos if (c & alvo).bit_count() >= acertos_alvo}
        
        # Algoritmo Guloso (Set Cover)
        while alvos_nao_cobertos:
            melhor_bilhete = None
            max_cobertura = -1
            alvos_cobertos_pelo_melhor = set()
            
            for candidato in universo_masks:
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
            
        # ----------------------------------------------------
        # Aplicação da FACA DA IA (Filtro K-Means Extremo)
        # ----------------------------------------------------
        msg_filtro = ""
        jogos_finais = jogos
        if estrategia == 'filtro_ia':
            kmeans_data = ml_kmeans.run_kmeans()
            if kmeans_data.get('status') == 'success':
                clima_id = kmeans_data.get('clima_atual', -1)
                perfil = kmeans_data['perfis_clusters'].get(str(clima_id))
                
                # Aplica a guilhotina em cada bilhete
                jogos_filtrados = []
                for jogo in jogos:
                    if engine_preditivo.e_jogo_perfeito_dinamico(jogo, perfil):
                        jogos_filtrados.append(jogo)
                
                msg_filtro = f"A IA destruiu {len(jogos) - len(jogos_filtrados)} jogos que não se encaixavam no Clima {clima_id}!"
                jogos_finais = jogos_filtrados
            
        return {
            "status": "success",
            "dezenas_base": melhores_18,
            "quantidade_jogos": len(jogos_finais),
            "jogos": jogos_finais,
            "economia_reais": (816 - len(jogos_finais)) * 3.50,
            "usa_ml": usa_ml,
            "estrategia_usada": estrategia,
            "msg_filtro": msg_filtro
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    estrategia = 'normal'
    if len(sys.argv) > 1:
        estrategia = sys.argv[1]
    print(json.dumps(gerar_fechamento(estrategia)))
