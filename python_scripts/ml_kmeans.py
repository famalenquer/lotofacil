import pymysql
import json
import pandas as pd
from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings('ignore')

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def extrar_macro_features(row):
    bolas = [row[f'b{i}'] for i in range(1, 16)]
    soma = sum(bolas)
    impares = sum(1 for b in bolas if b % 2 != 0)
    primos_base = {2, 3, 5, 7, 11, 13, 17, 19, 23}
    primos = sum(1 for b in bolas if b in primos_base)
    moldura_base = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    moldura = sum(1 for b in bolas if b in moldura_base)
    
    return {
        'concurso': row['concurso'],
        'soma': soma,
        'impares': impares,
        'primos': primos,
        'moldura': moldura
    }

def run_kmeans():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
            historico = cursor.fetchall()
            
            if len(historico) < 100:
                return {"status": "error", "message": "Dados insuficientes para clusterização."}
                
            dados_macro = [extrar_macro_features(row) for row in historico]
            df = pd.DataFrame(dados_macro)
            
            # Features usadas para clusterização
            X = df[['soma', 'impares', 'primos', 'moldura']]
            
            # K-Means com 4 "Climas" ou "Regimes"
            kmeans = KMeans(n_clusters=4, random_state=42)
            df['cluster'] = kmeans.fit_predict(X)
            
            # Analisar os perfis dos clusters
            perfis = {}
            for c in range(4):
                df_c = df[df['cluster'] == c]
                perfis[str(c)] = {
                    'qtd_sorteios': int(len(df_c)),
                    'media_soma': round(df_c['soma'].mean(), 1),
                    'media_impares': round(df_c['impares'].mean(), 1),
                    'media_primos': round(df_c['primos'].mean(), 1),
                    'media_moldura': round(df_c['moldura'].mean(), 1)
                }
                
            # O clima atual é definido pela moda (cluster mais frequente) dos últimos 10 concursos
            df_recentes = df.tail(10)
            clima_atual_id = int(df_recentes['cluster'].mode()[0])
            
            sorteios_recentes = []
            for _, r in df_recentes.iterrows():
                sorteios_recentes.append({
                    'concurso': int(r['concurso']),
                    'cluster': int(r['cluster'])
                })
                
            return {
                "status": "success",
                "clima_atual": clima_atual_id,
                "perfis_clusters": perfis,
                "ultimos_10": sorteios_recentes
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    print(json.dumps(run_kmeans()))
