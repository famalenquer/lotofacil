import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='lotofacil_db',
        cursorclass=pymysql.cursors.DictCursor
    )

conn = get_db_connection()
try:
    with conn.cursor() as cursor:
        cursor.execute("DESCRIBE concursos;")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col['Field']} - {col['Type']}")
        
        print("\n--- Amostra de Dados ---")
        cursor.execute("SELECT * FROM concursos LIMIT 1;")
        row = cursor.fetchone()
        if row:
            for k, v in row.items():
                print(f"{k}: {v}")
finally:
    conn.close()
