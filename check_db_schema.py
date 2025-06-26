import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

print('Tables in the database:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
for table in tables:
    print(f'\nTable: {table}')
    cursor.execute(f'PRAGMA table_info({table});')
    columns = cursor.fetchall()
    for col in columns:
        print(f'  {col[1]} ({col[2]})')

conn.close() 