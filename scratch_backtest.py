import pymysql
import sys
import os

# Precisamos importar o engine_preditivo.py para testar as funções
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_scripts'))
import engine_preditivo

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def backtest(concursos_para_testar=50):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Pega o histórico completo em ordem cronológica
            cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
            historico_completo = cursor.fetchall()
            
            total_concursos = len(historico_completo)
            if total_concursos < concursos_para_testar + 100:
                print("Histórico insuficiente para backtest.")
                return
                
            acertos_v7 = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 'abaixo_11': 0}
            acertos_v6 = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 'abaixo_11': 0}
            
            print(f"=== BACKTESTING: ÚLTIMOS {concursos_para_testar} CONCURSOS ===")
            print("Simulando a escolha de uma BASE DE 18 DEZENAS (O motor do fechamento)\n")
            
            for i in range(total_concursos - concursos_para_testar, total_concursos):
                # O sorteio que vamos tentar prever
                sorteio_alvo = historico_completo[i]
                dezenas_sorteadas = {sorteio_alvo[f'b{j}'] for j in range(1, 16)}
                
                # O conhecimento que a IA tinha ANTES deste sorteio (ordem DECRESCENTE igual o fetch_history original)
                historico_conhecido = list(reversed(historico_completo[:i]))
                
                # ------ TESTE V7 (Sazonalidade + Momentum) ------
                scores_v7, _ = engine_preditivo.calcular_scores_hibridos(historico_conhecido)
                dezenas_ordenadas_v7 = sorted(scores_v7.items(), key=lambda x: x[1], reverse=True)
                base_18_v7 = [x[0] for x in dezenas_ordenadas_v7[:18]]
                
                acerto_base_v7 = len(dezenas_sorteadas.intersection(set(base_18_v7)))
                if acerto_base_v7 >= 11:
                    acertos_v7[acerto_base_v7] += 1
                else:
                    acertos_v7['abaixo_11'] += 1
                    
                # ------ TESTE V6 (Sem Sazonalidade e Sem Momentum) ------
                # Vamos forçar a Sazonalidade e Momentum a 1.0 para simular a V6
                scores_estat, freq20, freq100 = engine_preditivo.calcular_pesos_estatisticos(historico_conhecido)
                max_score = max(scores_estat.values()) if scores_estat else 1
                
                scores_v6 = {}
                for dez in range(1, 26):
                    scores_v6[dez] = (scores_estat[dez] / max_score) * 100
                    
                dezenas_ordenadas_v6 = sorted(scores_v6.items(), key=lambda x: x[1], reverse=True)
                base_18_v6 = [x[0] for x in dezenas_ordenadas_v6[:18]]
                
                acerto_base_v6 = len(dezenas_sorteadas.intersection(set(base_18_v6)))
                if acerto_base_v6 >= 11:
                    acertos_v6[acerto_base_v6] += 1
                else:
                    acertos_v6['abaixo_11'] += 1
                    
            print("RESULTADOS DA BASE DE 18 DEZENAS (Quantos acertos a base conteve das 15 sorteadas)")
            print("-" * 50)
            print(f"{'Acertos':<10} | {'V6 (Estatística Pura)':<25} | {'V7 (Sazonal + Momentum)':<25}")
            print("-" * 50)
            for pt in [15, 14, 13, 12, 11, 'abaixo_11']:
                print(f"{pt:<10} | {acertos_v6[pt]:<25} | {acertos_v7[pt]:<25}")
            print("-" * 50)
            
            # Análise de Lucratividade Teórica Básica (Fechamento Econômico 6 jogos)
            # Se a base acerta 14, a chance de lucro no fechamento é altíssima.
            bons_jogos_v6 = acertos_v6[13] + acertos_v6[14] + acertos_v6[15]
            bons_jogos_v7 = acertos_v7[13] + acertos_v7[14] + acertos_v7[15]
            
            print(f"\nBases Fortes (13 a 15 pontos) em {concursos_para_testar} concursos:")
            print(f"Modelo V6: {bons_jogos_v6} vezes ({(bons_jogos_v6/concursos_para_testar)*100:.1f}%)")
            print(f"Modelo V7: {bons_jogos_v7} vezes ({(bons_jogos_v7/concursos_para_testar)*100:.1f}%)")
            
            if bons_jogos_v7 > bons_jogos_v6:
                print("\nCONCLUSÃO: O Algoritmo V7 SUPEROU a matemática antiga. Ele conseguiu encapsular mais dezenas sorteadas dentro da base escolhida.")
            else:
                print("\nCONCLUSÃO: O Algoritmo V7 não conseguiu superar a métrica antiga de forma expressiva neste recorte de curto prazo. Necessário calibrar pesos.")
            
    finally:
        conn.close()

if __name__ == "__main__":
    backtest(30)
