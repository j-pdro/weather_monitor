import sqlite3
from datetime import datetime, timedelta

DB_NAME = "weather_data.db"

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temperature (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            country TEXT,
            temperature REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_temperature(city, country, temperature):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO temperature (city, country, temperature) VALUES (?, ?, ?)",
                   (city, country, temperature))
    
    conn.commit()
    conn.close()

def get_last_temperature():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT temperature FROM temperature ORDER BY timestamp DESC LIMIT 1")
    last_temp = cursor.fetchone()
    
    conn.close()
    return last_temp[0] if last_temp else None

# Criar a tabela ao iniciar
create_table()
