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
    print("Conectando ao banco de dados e extraindo novas features...")
    conn = get_db_connection()
    query = "SELECT concurso, dezena, freq_20, freq_50, freq_100, freq_200, freq_total, atraso_norm, momentum, sazonalidade, target FROM ml_features ORDER BY concurso ASC"
    
    start_time = time.time()
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    conn.close()
    
    df = pd.DataFrame(result)
    
    if df.empty:
        print("Erro: A tabela ml_features está vazia.")
        return
        
    print(f"Extração concluída. Total de amostras: {len(df)}")
    
    features = ['dezena', 'freq_20', 'freq_50', 'freq_100', 'freq_200', 'freq_total', 'atraso_norm', 'momentum', 'sazonalidade']
    
    for col in features + ['target']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna()
    
    split_idx = int(len(df) * 0.8)
    
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]
    
    X_train = train_df[features]
    y_train = train_df['target']
    
    X_test = test_df[features]
    y_test = test_df['target']
    
    print("Treinando o RandomForestClassifier com as novas features...")
    
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    
    rf.fit(X_train, y_train)
    
    print("Modelo treinado! Avaliando acurácia no dataset de teste...")
    
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"\nAcurácia do Modelo: {acc * 100:.2f}%\n")
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))
    
    model_path = os.path.join(os.path.dirname(__file__), 'rf_model.pkl')
    joblib.dump(rf, model_path)
    
    print(f"Modelo avançado salvo com sucesso em: {model_path}")
    print(f"Tempo total de execução: {round(time.time() - start_time, 2)} segundos.")

if __name__ == "__main__":
    treinar_modelo()

