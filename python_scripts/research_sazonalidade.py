import pymysql
import pandas as pd
import datetime

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def run_research():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM concursos ORDER BY concurso ASC")
            data = cursor.fetchall()
            
            df = pd.DataFrame(data)
            
            if df.empty:
                print("No data.")
                return

            # Extract day of week and month
            df['data_sorteio'] = pd.to_datetime(df['data_sorteio'])
            df['dia_semana'] = df['data_sorteio'].dt.dayofweek # 0=Mon, 6=Sun
            df['mes'] = df['data_sorteio'].dt.month
            
            # Determine if it's accumulated (previous draw had 0 winners)
            # Shift the ganhadores_15_acertos to the next row to see if current draw is accumulated
            df['ganhadores_15_anterior'] = df['ganhadores_15_acertos'].shift(1)
            df['is_acumulado'] = df['ganhadores_15_anterior'] == 0
            
            # Calculate metrics: average sum
            soma_list = []
            for idx, row in df.iterrows():
                soma = sum([row[f'b{i}'] for i in range(1, 16)])
                soma_list.append(soma)
            df['soma'] = soma_list
            
            # Print analysis
            print("=== ANALISE DE ACUMULACAO ===")
            acumulado_stats = df.groupby('is_acumulado')['soma'].agg(['count', 'mean', 'std'])
            print(acumulado_stats)
            
            print("\n=== ANALISE DE DIA DA SEMANA ===")
            dow_stats = df.groupby('dia_semana')['soma'].agg(['count', 'mean', 'std'])
            print(dow_stats)
            
            print("\n=== ANALISE MENSAL ===")
            mes_stats = df.groupby('mes')['soma'].agg(['count', 'mean', 'std'])
            print(mes_stats)

    except Exception as e:
        print(e)
    finally:
        conn.close()

if __name__ == "__main__":
    run_research()
