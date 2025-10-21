#!/usr/bin/env python3
"""
Test completo del sistema SVXLink Statistics
"""

import os
import shutil
from datetime import datetime, date, timedelta
from database import DatabaseManager, DailyLogStats, CTCSSStats, TGStats
from log_processor import LogProcessor
from scheduler import LogScheduler

def create_test_data():
    """Crea dati di test nella directory data"""
    
    # Assicura che la directory data esista
    os.makedirs('data', exist_ok=True)
    
    # Copia il file di esempio se esiste
    if os.path.exists('sample.txt'):
        # Crea alcuni file di test con date diverse
        dates = [
            (date.today() - timedelta(days=2)).isoformat(),
            (date.today() - timedelta(days=1)).isoformat(),
            date.today().isoformat()
        ]
        
        for i, test_date in enumerate(dates):
            test_filename = f'data/svxlink_log_{test_date}.txt'
            shutil.copy('sample.txt', test_filename)
            print(f"📄 Creato file test: {test_filename}")
        
        return len(dates)
    else:
        print("⚠️ File sample.txt non trovato, creazione dati test limitata")
        return 0

def test_database():
    """Test del database"""
    print("\n🗄️ Test Database...")
    
    try:
        db = DatabaseManager('test_stats.db')
        
        # Test salvataggio statistiche
        test_stats = DailyLogStats(
            date="2025-10-21",
            filename="test_log.txt",
            file_size=1024,
            total_transmissions=50,
            total_transmission_time=3600,
            avg_transmission_time=72.0,
            max_transmission_time=300,
            min_transmission_time=5,
            total_qso=15,
            total_qso_time=1800
        )
        
        if db.save_daily_stats(test_stats):
            print("✅ Salvataggio statistiche giornaliere OK")
        
        # Test recupero
        stats = db.get_daily_stats("2025-10-21", "2025-10-21")
        if stats:
            print(f"✅ Recupero statistiche OK: {len(stats)} record")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test database: {e}")
        return False

def test_log_processor():
    """Test del processore log"""
    print("\n📄 Test Log Processor...")
    
    try:
        processor = LogProcessor('data', 'test_stats.db')
        
        # Ottieni riepilogo
        summary = processor.get_processing_summary()
        print(f"📊 File totali: {summary['total_files']}")
        print(f"📅 Date processate: {summary['processed_dates']}")
        print(f"⏳ File non processati: {summary['unprocessed_files']}")
        
        # Processa file se disponibili
        if summary['unprocessed_files'] > 0:
            result = processor.process_all_files()
            print(f"✅ Processati: {result['processed']} file, {result['errors']} errori")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test log processor: {e}")
        return False

def test_scheduler():
    """Test dello scheduler"""
    print("\n⏰ Test Scheduler...")
    
    try:
        scheduler = LogScheduler()
        
        # Test processamento avvio
        result = scheduler.process_on_startup()
        print(f"🚀 Processamento avvio: {result}")
        
        # Test job schedulati
        jobs = scheduler.get_next_runs()
        print(f"📅 Job schedulati: {len(jobs) if jobs else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test scheduler: {e}")
        return False

def test_statistics_queries():
    """Test delle query statistiche"""
    print("\n📊 Test Query Statistiche...")
    
    try:
        db = DatabaseManager('test_stats.db')
        
        # Test statistiche giornaliere
        today = date.today()
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()
        
        daily_stats = db.get_daily_stats(start_date, end_date)
        print(f"📅 Statistiche giornaliere (ultimi 7 giorni): {len(daily_stats)} record")
        
        # Test statistiche mensili
        monthly_stats = db.get_monthly_aggregated_stats(today.year, today.month)
        if monthly_stats:
            print(f"📆 Statistiche mensili: {monthly_stats.get('total_days', 0)} giorni")
        
        # Test date disponibili
        available_dates = db.get_available_dates()
        print(f"📋 Date disponibili nel database: {len(available_dates)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore test query: {e}")
        return False

def cleanup_test_files():
    """Pulizia file di test"""
    print("\n🧹 Pulizia file di test...")
    
    try:
        # Rimuovi database di test
        if os.path.exists('test_stats.db'):
            os.remove('test_stats.db')
            print("🗑️ Database di test rimosso")
        
        # Rimuovi file di test dalla directory data
        if os.path.exists('data'):
            for file in os.listdir('data'):
                if file.startswith('svxlink_log_') and file.endswith('.txt'):
                    file_path = os.path.join('data', file)
                    # Controlla se è un file di test (date recenti)
                    if any(recent_date in file for recent_date in [
                        (date.today() - timedelta(days=2)).isoformat(),
                        (date.today() - timedelta(days=1)).isoformat(),
                        date.today().isoformat()
                    ]):
                        os.remove(file_path)
                        print(f"🗑️ File di test rimosso: {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore pulizia: {e}")
        return False

def main():
    """Test principale"""
    print("🧪 SVXLink Statistics - Test Suite Completo")
    print("=" * 50)
    
    # Contatori risultati
    tests_passed = 0
    tests_total = 0
    
    # Crea dati di test
    print("📋 Preparazione dati di test...")
    created_files = create_test_data()
    print(f"📄 Creati {created_files} file di test")
    
    # Esegui test
    test_functions = [
        ("Database", test_database),
        ("Log Processor", test_log_processor),
        ("Scheduler", test_scheduler),
        ("Query Statistiche", test_statistics_queries)
    ]
    
    for test_name, test_func in test_functions:
        tests_total += 1
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if test_func():
                tests_passed += 1
                print(f"✅ {test_name} - PASSATO")
            else:
                print(f"❌ {test_name} - FALLITO")
        except Exception as e:
            print(f"💥 {test_name} - ERRORE: {e}")
    
    # Riepilogo
    print("\n" + "="*50)
    print("📊 RIEPILOGO TEST")
    print(f"✅ Test passati: {tests_passed}/{tests_total}")
    print(f"❌ Test falliti: {tests_total - tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("🎉 TUTTI I TEST SONO PASSATI!")
    else:
        print("⚠️ Alcuni test sono falliti. Controlla i log sopra.")
    
    # Pulizia
    if input("\n🧹 Vuoi pulire i file di test? (y/N): ").lower() == 'y':
        cleanup_test_files()
        print("✨ Pulizia completata")
    
    print("\n🏁 Test suite completato!")

if __name__ == "__main__":
    main()