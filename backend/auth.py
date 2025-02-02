import pyodbc

conn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};'
                      'SERVER=netbot-sql-server.database.windows.net;'
                      'PORT=1433;'
                      'DATABASE=netbot-db;'
                      'UID=Admins1;'
                      'PWD=Testadmin@123')

cursor = conn.cursor()
cursor.execute('SELECT 1')
print(cursor.fetchone())
conn.close()
