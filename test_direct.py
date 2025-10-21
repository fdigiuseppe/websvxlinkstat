#!/usr/bin/env python3
"""
Test diretto per verificare se il processamento funziona
"""

import sys
import os
from pathlib import Path

# Aggiungi il percorso corrente al path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_direct_processing():
    """Test diretto del processamento senza variabili globali"""
    
    try:
        print("🔧 Importazione moduli...")
        from database import DatabaseManager
        from log_processor import LogProcessor
        
        print("✅ Moduli importati")
        
        # Test diretto
        print("📊 Inizializzazione componenti...")
        log_processor = LogProcessor()
        
        print("🔍 Verifica file disponibili...")
        data_dir = Path("data")
        log_files = list(data_dir.glob("svxlink_log_*.txt"))
        print(f"   📁 File trovati: {[f.name for f in log_files]}")
        
        if not log_files:
            print("❌ Nessun file di log trovato!")
            return False
            
        # Test su un singolo file
        test_file = log_files[0]
        print(f"\n🧪 Test su file: {test_file.name}")
        
        # Leggi contenuto
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print(f"   📄 Dimensione file: {len(content)} caratteri")
        print(f"   📝 Prime righe: {content[:200]}...")
        
        # Test analyzer direttamente
        from app import SVXLinkLogAnalyzer
        analyzer = SVXLinkLogAnalyzer()
        
        print("\n⚙️ Test analisi log...")
        result = analyzer.analyze_log(content)
        
        print(f"✅ Analisi completata!")
        print(f"   🔑 Keys disponibili: {list(result.keys())}")
        
        if 'talk_groups' in result:
            print(f"   💬 talk_groups OK: {len(result['talk_groups']['tg_list'])} TG trovati")
        else:
            print("   ❌ talk_groups mancante!")
            
        if 'basic' in result:
            basic = result['basic']
            print(f"   📊 Basic stats: {basic['total_transmissions']} trasmissioni")
        else:
            print("   ❌ basic stats mancanti!")
        
        # Test processamento completo
        print(f"\n🚀 Test processamento file...")
        success = log_processor.process_single_file(test_file)
        
        if success:
            print("✅ File processato con successo!")
            
            # Verifica database
            dates = log_processor.db_manager.get_available_dates()
            print(f"   📅 Date nel database: {len(dates)}")
            if dates:
                print(f"   📊 Prime date: {dates[:3]}")
        else:
            print("❌ Errore nel processamento!")
            
        return success
        
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Test Diretto Processamento Log")
    print("=" * 40)
    
    success = test_direct_processing()
    
    print("=" * 40)
    print("✅ Test completato!" if success else "❌ Test fallito!")