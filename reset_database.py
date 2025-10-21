#!/usr/bin/env python3
"""
Script per resettare il database SVXLink Log Analyzer
Elimina tutti i dati e ricrea lo schema
"""

import os
import sys
from database import DatabaseManager

def main():
    """Funzione principale"""
    print("🔄 SVXLink Database Reset Tool")
    print("=" * 50)
    
    # Ottieni path database da variabile d'ambiente o usa default
    db_path = os.getenv('DATABASE_PATH', 'data/svxlink_stats.db')
    print(f"📁 Database path: {db_path}")
    
    # Verifica se il database esiste
    if not os.path.exists(db_path):
        print(f"⚠️ File database non trovato: {db_path}")
        print("✅ Niente da resettare")
        return
    
    # Chiedi conferma
    print("\n⚠️ ATTENZIONE: Questa operazione eliminerà TUTTI i dati nel database!")
    print(f"Database: {os.path.abspath(db_path)}")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("🚀 Flag --force rilevato, procedo senza conferma...")
        confirm = 'y'
    else:
        confirm = input("\nSei sicuro di voler continuare? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Operazione annullata")
        return
    
    try:
        # Inizializza database manager
        print("\n🔧 Inizializzo database manager...")
        db_manager = DatabaseManager(db_path)
        
        # Mostra statistiche prima del reset
        try:
            dates = db_manager.get_available_dates()
            range_info = db_manager.get_date_range_stats()
            print(f"📊 Date disponibili: {len(dates)}")
            if range_info.get('first_date'):
                print(f"📅 Primo record: {range_info['first_date']}")
                print(f"📅 Ultimo record: {range_info['last_date']}")
                print(f"📈 Giorni totali: {range_info.get('total_days', 0)}")
        except Exception as e:
            print(f"⚠️ Impossibile leggere statistiche correnti: {e}")
        
        # Esegui reset
        print("\n🗑️ Resetto database...")
        deleted_count = db_manager.reset_database()
        
        print("\n✅ Reset completato!")
        print(f"🧹 Record eliminati: {deleted_count}")
        print("🆕 Schema ricreato")
        
        # Verifica che il database sia vuoto
        dates_after = db_manager.get_available_dates()
        print(f"✓ Date dopo reset: {len(dates_after)} (dovrebbe essere 0)")
        
    except Exception as e:
        print(f"\n❌ Errore durante il reset: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()