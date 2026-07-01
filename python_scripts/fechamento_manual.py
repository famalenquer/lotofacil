import json
import sys
import itertools
import os

def gerar_fechamento_manual(payload_file):
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        estrategia = data.get('estrategia', 'normal')
        dezenas_base = data.get('dezenas_base', [])
        dezenas_fixas = data.get('dezenas_fixas', [])
        
        acertos_alvo = 14
        if estrategia == 'economico' or estrategia == 'diamante_economico' or estrategia == 'diamante_supremo':
            acertos_alvo = 13
            
        # Ensure they are sorted
        dezenas_base = sorted(dezenas_base)
        dezenas_fixas = sorted(dezenas_fixas)
        
        num_fixas = len(dezenas_fixas)
        dezenas_variaveis = dezenas_base
        
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
            
        jogos = sorted(jogos)
        
        return {
            "status": "success",
            "dezenas_base": dezenas_base,
            "dezenas_fixas": dezenas_fixas,
            "quantidade_jogos": len(jogos),
            "jogos": jogos,
            "estrategia_usada": estrategia,
            "economia_reais": (3268760 - len(jogos)) * 3.50
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Missing payload file"}))
        sys.exit(1)
        
    payload_file = sys.argv[1]
    resultado = gerar_fechamento_manual(payload_file)
    print(json.dumps(resultado))
