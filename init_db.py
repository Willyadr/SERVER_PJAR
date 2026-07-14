import sqlite3

def buat_database():
    # Membuat koneksi (akan otomatis membuat file database.db jika belum ada)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Membuat tabel users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[✔] Database dan tabel 'users' berhasil dibuat!")

if __name__ == '__main__':
    buat_database()