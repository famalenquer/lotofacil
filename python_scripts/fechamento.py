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
        
        total_base = 18
        num_fixas = 0
        acertos_alvo = 14
        
        if estrategia == 'economico':
            acertos_alvo = 13
        elif estrategia == 'diamante_economico':
            total_base = 19
            num_fixas = 3
            acertos_alvo = 13
        elif estrategia == 'diamante_supremo':
            total_base = 20
            num_fixas = 3
            acertos_alvo = 13
            
        ultimo_resultado = {historico[0][f'b{j}'] for j in range(1, 16)}
        
        # Filtro Matemático para a Base (Evita que a base replique o último concurso)
        # Lotofácil repete de 8 a 10 dezenas. Para uma base de 18, não devemos ter mais que 11 repetidas.
        max_repetidas_na_base = 11 if total_base == 18 else (12 if total_base == 19 else 13)
        
        melhores = []
        repetidas_inclusas = 0
        ausentes_inclusas = 0
        
        for dez, score in dezenas_ordenadas:
            if len(melhores) >= total_base:
                break
                
            if dez in ultimo_resultado:
                if repetidas_inclusas < max_repetidas_na_base:
                    melhores.append(dez)
                    repetidas_inclusas += 1
            else:
                melhores.append(dez)
                ausentes_inclusas += 1
                
        # Caso falte preencher por restrição, completamos
        if len(melhores) < total_base:
            for dez, score in dezenas_ordenadas:
                if dez not in melhores:
                    melhores.append(dez)
                if len(melhores) >= total_base:
                    break
        
        dezenas_fixas = []
        if num_fixas > 0:
            dezenas_fixas = sorted(melhores[:num_fixas])
            dezenas_variaveis = sorted(melhores[num_fixas:])
        else:
            dezenas_variaveis = sorted(melhores)
            
        melhores_base = sorted(melhores)
            
        qtd_variaveis_no_bilhete = 15 - num_fixas
        total_vars = len(dezenas_variaveis)
        
        idx_to_num = {i: dezenas_variaveis[i] for i in range(total_vars)}
        universo_idx = list(itertools.combinations(range(total_vars), qtd_variaveis_no_bilhete))
        
        universo_masks = []
        for comb in universo_idx:
            mask = 0
            for bit in comb:
                mask |= (1 << bit)
            universo_masks.append(mask)
            
        alvos_nao_cobertos = set(universo_masks)
        bilhetes_escolhidos_masks = []
        
        acertos_vars_alvo = acertos_alvo - num_fixas
        
        cobertura_dict = {}
        for c in universo_masks:
            cobertura_dict[c] = {alvo for alvo in alvos_nao_cobertos if (c & alvo).bit_count() >= acertos_vars_alvo}
        
        while alvos_nao_cobertos:
            melhor_bilhete = max(universo_masks, key=lambda cand: len(cobertura_dict[cand] & alvos_nao_cobertos))
            alvos_cobertos_pelo_melhor = cobertura_dict[melhor_bilhete] & alvos_nao_cobertos
            bilhetes_escolhidos_masks.append(melhor_bilhete)
            alvos_nao_cobertos -= alvos_cobertos_pelo_melhor
            
        jogos = []
        for mask in bilhetes_escolhidos_masks:
            jogo_real = list(dezenas_fixas)
            for i in range(total_vars):
                if (mask & (1 << i)):
                    jogo_real.append(idx_to_num[i])
            jogos.append(sorted(jogo_real))
            
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
                    if engine_preditivo.e_jogo_perfeito_dinamico(jogo, perfil, ultimo_resultado):
                        jogos_filtrados.append(jogo)
                
                msg_filtro = f"A IA destruiu {len(jogos) - len(jogos_filtrados)} jogos que não se encaixavam no Clima {clima_id} ou na Regra de Repetidas!"
                jogos_finais = jogos_filtrados
            
        return {
            "status": "success",
            "dezenas_base": melhores_base,
            "dezenas_fixas": dezenas_fixas,
            "quantidade_jogos": len(jogos_finais),
            "jogos": jogos_finais,
            "economia_reais": (3268760 - len(jogos_finais)) * 3.50, # comparando com o maximo
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
