import sys
import json
import pymysql

# Importa o motor preditivo para calcular scores historicos
import engine_preditivo
import correlacao

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def gerar_diagnostico(payload_json):
    try:
        data = json.loads(payload_json)
        
        concurso_alvo = data.get('concurso_alvo')
        sorteadas = set(data.get('sorteadas', []))
        base = set(data.get('dezenas_base', []))
        fixas = set(data.get('dezenas_fixas', []))
        estrategia = data.get('nome_estrategia', '').lower()
        custo = data.get('custo', 0)
        lucro = data.get('lucro', 0)
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM concursos WHERE concurso < %s ORDER BY concurso DESC", (concurso_alvo,))
                historico = cursor.fetchall()
                
                cursor.execute("SELECT data_sorteio FROM concursos WHERE concurso = %s", (concurso_alvo,))
                sorteio_alvo = cursor.fetchone()
                dia_alvo = sorteio_alvo['data_sorteio'].weekday() if sorteio_alvo and sorteio_alvo.get('data_sorteio') else None
        finally:
            conn.close()
            
        diagnosticos = []
        sorteadas_fora_base = sorteadas - base
        fixas_erradas = fixas - sorteadas
        acertos_base = len(sorteadas.intersection(base))
        
        # --- LÓGICA DE RACIOCÍNIO POR ESTRATÉGIA ---
        
        if "diamante" in estrategia:
            # 💎 DIAMANTE (Supremo ou Econômico)
            if len(fixas_erradas) > 0:
                diagnosticos.append({
                    "tipo": "danger",
                    "titulo": "Erro Crítico nas Fixas",
                    "mensagem": f"Você errou {len(fixas_erradas)} dezenas fixas ({', '.join(map(lambda x: str(x).zfill(2), sorted(fixas_erradas)))}). Na estratégia Diamante, o fechamento exige 100% de acerto nas fixas para garantir lucro. Esse erro desestruturou a matriz de combinações."
                })
            else:
                diagnosticos.append({
                    "tipo": "success",
                    "titulo": "Fixas Cravadas (Diamante)!",
                    "mensagem": "Você executou a estratégia Diamante com perfeição na fundação! Ao acertar todas as fixas, você garantiu que o fechamento trabalhasse a seu favor."
                })
                
        elif "filtro" in estrategia or "faca" in estrategia:
            # 🤖 FILTRO DA IA (K-Means)
            diagnosticos.append({
                "tipo": "info",
                "titulo": "Filtro de Machine Learning Ativo",
                "mensagem": "Nesta aposta você utilizou a 'Faca da IA' para reduzir os 24 jogos base cortando os que não tinham o 'Clima K-Means' do dia."
            })
            if acertos_base >= 14 and lucro < 0:
                diagnosticos.append({
                    "tipo": "warning",
                    "titulo": "A Faca Cortou o Prêmio",
                    "mensagem": f"Infelizmente, você acertou {acertos_base} na base, o que geraria um prêmio altíssimo no fechamento normal. Mas o bilhete premiado não passou pelo crivo do Machine Learning. O sorteio fugiu do padrão estatístico esperado pela IA."
                })
            elif acertos_base < 14:
                diagnosticos.append({
                    "tipo": "success",
                    "titulo": "Corte Inteligente",
                    "mensagem": "Sua base não pontuou o suficiente, então o filtro do Machine Learning te salvou dinheiro cortando jogos que já estariam perdidos de qualquer forma."
                })
                
        elif "econômico" in estrategia:
            # 💸 ECONÔMICO (Base 18, 6 jogos)
            diagnosticos.append({
                "tipo": "warning",
                "titulo": "Risco Assumido (Fechamento Reduzido)",
                "mensagem": "Você utilizou o fechamento Econômico. A matemática aqui não garante os 14 pontos (garantia cai para 13). Essa economia de bilhetes justifica o retorno menor."
            })
            if acertos_base == 14 and lucro < 30:
                diagnosticos.append({
                    "tipo": "danger",
                    "titulo": "Vítima da Matriz Reduzida",
                    "mensagem": "Você acertou 14 na base! Se tivesse jogado o Normal (24 jogos), teria pego os 14 pontos. Como economizou jogando apenas 6, o prêmio escapou pelas frestas da matriz."
                })
                
        else:
            # 🎯 NORMAL (Base 18, 24 jogos, sem fixas)
            if acertos_base < 12:
                diagnosticos.append({
                    "tipo": "danger",
                    "titulo": "Desperdício Financeiro",
                    "mensagem": f"Você gastou R$ {custo:.2f} num fechamento robusto de 24 jogos, mas acertou apenas {acertos_base} dezenas na base. Fechamentos caros exigem bases afiadas. Focar melhor nas tendências antes de abrir a carteira é crucial."
                })
            elif acertos_base >= 14:
                diagnosticos.append({
                    "tipo": "success",
                    "titulo": "Matemática Honrada",
                    "mensagem": "Você cumpriu a condição de acerto da base (14 em 18) num fechamento sem filtros. A garantia matemática foi executada exatamente como projetada."
                })

        # --- LÓGICA GERAL PARA QUALQUER ESTRATÉGIA ---
        if len(sorteadas_fora_base) > 0:
            pontuacao_teto = 15 - len(sorteadas_fora_base)
            diagnosticos.append({
                "tipo": "warning",
                "titulo": "Teto da Base Rebaixado",
                "mensagem": f"Das 15 dezenas sorteadas, {len(sorteadas_fora_base)} ficaram de fora da sua seleção ({', '.join(map(lambda x: str(x).zfill(2), sorted(sorteadas_fora_base)))}). Seu teto matemático caiu para {pontuacao_teto} pontos logo no início."
            })
            
        # Análise de Comportamento (Motor V7)
        if historico:
            scores_v7, _ = engine_preditivo.calcular_scores_hibridos(historico, dia_alvo)
            
            # Recuperar dezenas do concurso anterior ao alvo para saber o que era "repetida"
            ultimo_sorteio_antes_do_alvo = {historico[0][f'b{i}'] for i in range(1, 16)}

            # Dezenas Quentes que ele ignorou
            dezenas_quentes = sorted(scores_v7.items(), key=lambda x: x[1], reverse=True)[:10]
            quentes_ignoradas = [d[0] for d in dezenas_quentes if d[0] not in base and d[0] in sorteadas]
            
            if quentes_ignoradas:
                quentes_repetidas_ignoradas = [d for d in quentes_ignoradas if d in ultimo_sorteio_antes_do_alvo]
                quentes_ausentes_ignoradas = [d for d in quentes_ignoradas if d not in ultimo_sorteio_antes_do_alvo]
                
                if ("diamante" in estrategia or "normal" in estrategia or "econômico" in estrategia) and quentes_repetidas_ignoradas:
                    diagnosticos.append({
                        "tipo": "success",
                        "titulo": "Filtro de Repetidas Aplicado com Sucesso",
                        "mensagem": f"O sistema excluiu propositalmente as dezenas quentes ({', '.join(map(lambda x: str(x).zfill(2), quentes_repetidas_ignoradas))}) para não estourar o limite matemático de repetidas do concurso anterior. Ótima decisão algorítmica."
                    })
                
                if quentes_ausentes_ignoradas or (not quentes_repetidas_ignoradas):
                    if not quentes_ausentes_ignoradas: quentes_ausentes_ignoradas = quentes_ignoradas
                    diagnosticos.append({
                        "tipo": "info",
                        "titulo": "Tendência (Momentum) Ignorada",
                        "mensagem": f"O fechamento deixou de fora dezenas fortíssimas como {', '.join(map(lambda x: str(x).zfill(2), quentes_ausentes_ignoradas))}. O Motor V7 apontava essas dezenas com alto Momentum."
                    })
                
            # Dezenas Frias que ele insistiu
            dezenas_frias = sorted(scores_v7.items(), key=lambda x: x[1])[:10]
            frias_escolhidas = [d[0] for d in dezenas_frias if d[0] in base and d[0] not in sorteadas]
            
            if frias_escolhidas:
                if len(base) >= 19:
                    diagnosticos.append({
                        "tipo": "info",
                        "titulo": "Dezenas Frias Necessárias",
                        "mensagem": f"Para montar uma base gigante de {len(base)} dezenas (cobrindo 80% do volante), o algoritmo precisou aceitar algumas dezenas frias ({', '.join(map(lambda x: str(x).zfill(2), frias_escolhidas))}). Isso é um sacrifício matemático padrão das estratégias agressivas."
                    })
                else:
                    diagnosticos.append({
                        "tipo": "info",
                        "titulo": "Insistência em Dezenas Frias",
                        "mensagem": f"Sua base contou com dezenas como {', '.join(map(lambda x: str(x).zfill(2), frias_escolhidas))} que não saíram. O Motor V7 já apontava que elas estavam congelando."
                    })

        return {
            "status": "success",
            "diagnosticos": diagnosticos
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        try:
            import os
            if os.path.exists(arg):
                with open(arg, 'r', encoding='utf-8') as f:
                    payload = f.read()
            else:
                payload = arg
            print(json.dumps(gerar_diagnostico(payload)))
        except Exception as e:
            print(json.dumps({"status": "error", "message": f"Erro de I/O: {str(e)}"}))
    else:
        print(json.dumps({"status": "error", "message": "Nenhum payload recebido"}))
