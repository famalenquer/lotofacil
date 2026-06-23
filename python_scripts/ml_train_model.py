import pymysql
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import time
import os

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

def treinar_modelo():
    print("Conectando ao banco de dados e extraindo features...")
    conn = get_db_connection()
    query = "SELECT concurso, dezena, freq_20, freq_100, atraso, target FROM ml_features ORDER BY concurso ASC"
    
    start_time = time.time()
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(result)
    
    # Converter colunas para numérico forçadamente
    for col in ['dezena', 'freq_20', 'freq_100', 'atraso', 'target']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna()
    
    if df.empty:
        print("Erro: A tabela ml_features está vazia.")
        return
        
    print(f"Extração concluída. Total de amostras: {len(df)}")
    
    # Prepara as variáveis
    # A variável 'concurso' é temporal, usamos para separar treino e teste
    # Features (X): dezena, freq_20, freq_100, atraso
    # Target (y): target (1 saiu, 0 falhou)
    
    # Split Temporal (Treina com os concursos mais antigos, testa com os 20% mais recentes)
    split_idx = int(len(df) * 0.8)
    
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    features = ['dezena', 'freq_20', 'freq_100', 'atraso']
    
    X_train = train_df[features]
    y_train = train_df['target']
    
    X_test = test_df[features]
    y_test = test_df['target']
    
    print("Treinando o RandomForestClassifier (isso pode levar de 10 a 30 segundos)...")
    
    # Configuração do modelo:
    # 100 árvores, e n_jobs=-1 para usar todos os núcleos do processador
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    
    rf.fit(X_train, y_train)
    
    print("Modelo treinado! Avaliando acurácia no dataset de teste invisível...")
    
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\nAcurácia do Modelo: {acc * 100:.2f}%\n")
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))
    
    # Salvando o modelo na pasta
    model_path = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
    joblib.dump(rf, model_path)
    
    print(f"Modelo salvo com sucesso em: {model_path}")
    print(f"Tempo total de execução: {round(time.time() - start_time, 2)} segundos.")

if __name__ == "__main__":
    treinar_modelo()
