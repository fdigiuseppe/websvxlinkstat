#!/usr/bin/env python3
"""
Script di migrazione database per SVXLink Log Analyzer
Aggiunge tabelle mancanti senza perdere dati esistenti
"""

import os
import sqlite3
import sys

def table_exists(cursor, table_name):
    """Verifica se una tabella esiste"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def migrate_database(db_path):
    """Esegue migrazioni necessarie sul database"""
    print("🔄 SVXLink Database Migration Tool")
    print("=" * 50)
    print(f"📁 Database: {db_path}")
    
    if not os.path.exists(db_path):
        print("⚠️ Database non trovato - verrà creato al primo avvio")
        return 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        migrations_done = 0
        
        # Migrazione 1: Tabella daily_disconnections
        if not table_exists(cursor, 'daily_disconnections'):
            print("\n📝 Creazione tabella 'daily_disconnections'...")
            cursor.execute("""
                CREATE TABLE daily_disconnections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    log_date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER,
                    disconnection_count INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'ongoing'
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_disconnections_date 
                ON daily_disconnections(log_date)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_disconnections_status 
                ON daily_disconnections(status)
            """)
            print("✅ Tabella 'daily_disconnections' creata con successo")
            migrations_done += 1
        else:
            print("✓ Tabella 'daily_disconnections' già presente")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print(f"✅ Migrazione completata! ({migrations_done} modifiche applicate)")
        return 0
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante la migrazione: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Errore inaspettato: {e}")
        return 1

def main():
    """Funzione principale"""
    # Ottieni path database da variabile d'ambiente o usa default
    db_path = os.getenv('DATABASE_PATH', 'data/svxlink_stats.db')
    
    # Esegui migrazioni
    exit_code = migrate_database(db_path)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
