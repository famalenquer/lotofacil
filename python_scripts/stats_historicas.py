import pymysql
import json

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def run_historico(historico_data=None):
    if historico_data is not None:
        # Se for injetado de fora (ex: engine_preditivo rodando no modo simulação do diagnóstico),
        # verifica se precisa inverter para ASCendente
        if len(historico_data) > 1 and historico_data[0]['concurso'] > historico_data[-1]['concurso']:
            historico = list(reversed(historico_data))
        else:
            historico = historico_data
        
        # Pula a conexão
        return _process_historico(historico)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
            historico = cursor.fetchall()
            return _process_historico(historico)
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()

def _process_historico(historico):
    try:
            
            # Arrays para atraso
            ultimo_visto = {i: 0 for i in range(1, 26)}
            maior_atraso = {i: 0 for i in range(1, 26)}
            freq = {i: 0 for i in range(1, 26)}
            
            maior_sequencia_global = 0
            concurso_maior_seq = 0
            seq_vencedora = []
            
            for row in historico:
                c = row['concurso']
                bolas = sorted([row[f'b{i}'] for i in range(1, 16)])
                
                # Calcular maior sequencia no bilhete
                seq_atual = 1
                max_seq_local = 1
                seq_temporaria = [bolas[0]]
                seq_max_local_arr = [bolas[0]]
                
                for i in range(1, 15):
                    if bolas[i] == bolas[i-1] + 1:
                        seq_atual += 1
                        seq_temporaria.append(bolas[i])
                        if seq_atual > max_seq_local:
                            max_seq_local = seq_atual
                            seq_max_local_arr = list(seq_temporaria)
                    else:
                        seq_atual = 1
                        seq_temporaria = [bolas[i]]
                        
                if max_seq_local > maior_sequencia_global:
                    maior_sequencia_global = max_seq_local
                    concurso_maior_seq = c
                    seq_vencedora = seq_max_local_arr
                
                for dez in range(1, 26):
                    if dez in bolas:
                        freq[dez] += 1
                        atraso = c - ultimo_visto[dez] - 1
                        if ultimo_visto[dez] > 0 and atraso > maior_atraso[dez]:
                            maior_atraso[dez] = atraso
                        ultimo_visto[dez] = c
            
            # Atraso atual
            ultimo_concurso = historico[-1]['concurso']
            atraso_atual = {dez: ultimo_concurso - ultimo_visto[dez] for dez in range(1, 26)}
            
            # Montar resposta
            res_atrasos = []
            for dez in range(1, 26):
                res_atrasos.append({
                    "dezena": dez,
                    "maior_atraso_historico": maior_atraso[dez],
                    "atraso_atual": atraso_atual[dez],
                    "risco_quebra": atraso_atual[dez] >= maior_atraso[dez] and atraso_atual[dez] > 0
                })
            
            # Ordenar
            res_atrasos = sorted(res_atrasos, key=lambda x: x['maior_atraso_historico'], reverse=True)
            
            # Top 5
            top_5 = sorted([{"dezena": k, "freq": v} for k, v in freq.items()], key=lambda x: x['freq'], reverse=True)[:5]
            
            return {
                "status": "success",
                "top_5": top_5,
                "maior_sequencia": maior_sequencia_global,
                "concurso_maior_seq": concurso_maior_seq,
                "seq_vencedora": seq_vencedora,
                "atrasos": res_atrasos
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(json.dumps(run_historico()))
