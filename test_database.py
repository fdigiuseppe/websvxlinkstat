#!/usr/bin/env python3
"""
Test di connettività database per diagnosticare problemi in produzione
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database():
    print("🔍 Test Database SVXLink Statistics")
    print("=" * 50)
    
    # Test 1: Importazione moduli
    try:
        from database import DatabaseManager
        print("✅ Import DatabaseManager: OK")
    except Exception as e:
        print(f"❌ Import DatabaseManager: ERRORE - {e}")
        return False
    
    # Test 2: Inizializzazione DatabaseManager
    try:
        db = DatabaseManager()
        print("✅ Inizializzazione DatabaseManager: OK")
    except Exception as e:
        print(f"❌ Inizializzazione DatabaseManager: ERRORE - {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False
    
    # Test 3: Verifica connessione database
    try:
        db.get_date_range_stats()
        print("✅ Connessione database: OK")
    except Exception as e:
        print(f"❌ Connessione database: ERRORE - {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False
    
    # Test 4: Verifica struttura tabelle
    try:
        # Controlla se le tabelle principali esistono
        cursor = db.conn.cursor()
        
        tables_to_check = ['daily_logs', 'daily_ctcss_stats', 'daily_tg_stats', 'monthly_stats', 'yearly_stats']
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Tabella {table}: {count} record")
            
    except Exception as e:
        print(f"❌ Verifica tabelle: ERRORE - {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False
    
    # Test 5: Test path e permessi
    try:
        db_path = db.db_path
        print(f"📁 Path database: {db_path}")
        print(f"📄 File esiste: {os.path.exists(db_path)}")
        if os.path.exists(db_path):
            print(f"📊 Dimensione file: {os.path.getsize(db_path)} bytes")
            print(f"🔓 Leggibile: {os.access(db_path, os.R_OK)}")
            print(f"✍️ Scrivibile: {os.access(db_path, os.W_OK)}")
    except Exception as e:
        print(f"❌ Verifica path/permessi: ERRORE - {e}")
    
    print("\n🎉 Test database completato con successo!")
    return True

def test_flask_integration():
    print("\n🔍 Test Integrazione Flask")
    print("=" * 50)
    
    try:
        import app
        print("✅ Import app Flask: OK")
        
        # Test della funzione di verifica
        available = app.is_database_available()
        print(f"✅ is_database_available(): {available}")
        
        if not available:
            print("⚠️ La funzione dice che il database non è disponibile")
            print(f"DB_AVAILABLE: {app.DB_AVAILABLE}")
            print(f"db_manager is None: {app.db_manager is None}")
            
    except Exception as e:
        print(f"❌ Test Flask: ERRORE - {e}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Diagnostica Database SVXLink Statistics\n")
    
    success = True
    success &= test_database()
    success &= test_flask_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Tutti i test sono passati!")
    else:
        print("⚠️ Alcuni test hanno avuto problemi.")
    
    sys.exit(0 if success else 1)