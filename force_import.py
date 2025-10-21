#!/usr/bin/env python3
"""
Script per forzare l'importazione iniziale dei file di log
"""

import os
import sys
from pathlib import Path

# Aggiungi il percorso corrente al path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def force_import():
    """Forza l'importazione dei file di log presenti nella cartella data"""
    
    try:
        # Import con gestione errori
        print("🔧 Inizializzazione moduli...")
        
        from database import DatabaseManager
        from log_processor import LogProcessor
        
        print("✅ Moduli importati correttamente")
        
        # Inizializza log processor (che inizializzerà anche il database manager)
        print("� Inizializzazione log processor...")
        log_processor = LogProcessor()
        
        # Ottieni reference al database manager
        db_manager = log_processor.db_manager
        
        # Lista file disponibili
        data_dir = Path("data")
        log_files = list(data_dir.glob("svxlink_log_*.txt"))
        
        print(f"📁 Trovati {len(log_files)} file di log:")
        for file in log_files:
            print(f"   - {file.name}")
        
        # Forza processamento di tutti i file
        print("\n🚀 Avvio processamento forzato...")
        result = log_processor.process_all_files(force=True)
        
        print(f"\n✅ Processamento completato:")
        print(f"   📊 File processati: {result['processed']}")
        print(f"   ❌ Errori: {result['errors']}")
        
        if result['errors'] > 0:
            print(f"\n⚠️ Dettagli errori:")
            for error in result.get('error_details', []):
                print(f"   - {error}")
        
        # Verifica statistiche disponibili
        print("\n📈 Verifica statistiche disponibili...")
        dates = db_manager.get_available_dates()
        print(f"   📅 Date disponibili: {len(dates)}")
        
        if dates:
            print("   Prima data:", min(dates))
            print("   Ultima data:", max(dates))
            
            # Mostra alcune statistiche di esempio
            date_range = db_manager.get_date_range_stats()
            print(f"   📊 Range statistiche: {date_range}")
        else:
            print("   ⚠️ Nessuna statistica disponibile nel database")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante l'importazione: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 SVXLink Log Analyzer - Importazione Forzata")
    print("=" * 50)
    
    success = force_import()
    
    print("=" * 50)
    if success:
        print("✅ Importazione completata con successo!")
    else:
        print("❌ Importazione fallita!")
    
    sys.exit(0 if success else 1)