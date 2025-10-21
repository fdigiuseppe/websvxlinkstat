#!/usr/bin/env python3
"""
Test rapido per verificare il funzionamento dell'app Flask SVXLink Statistics
"""
import sys
import os
import tempfile
import shutil
from datetime import datetime

# Aggiungi il percorso dell'app Flask
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """Test di base per verificare che i moduli si importino correttamente"""
    print("🧪 Test importazione moduli...")
    
    try:
        import app
        print("✅ Flask app importata correttamente")
    except Exception as e:
        print(f"❌ Errore importazione app: {e}")
        return False
        
    try:
        # Test inizializzazione Flask app
        flask_app = app.app
        print("✅ Flask app inizializzata")
    except Exception as e:
        print(f"❌ Errore inizializzazione Flask: {e}")
        return False
    
    return True

def test_log_analysis():
    """Test dell'analisi dei log"""
    print("\n📄 Test analisi log...")
    
    try:
        from app import analyze_log_content
        
        # Usa il file di log esistente
        log_file = "data/svxlink_log_2025-10-19.txt"
        if not os.path.exists(log_file):
            print("❌ File di log non trovato")
            return False
            
        with open(log_file, 'r') as f:
            content = f.read()
        
        results = analyze_log_content(content)
        
        print(f"✅ Analisi completata:")
        print(f"   - Trasmissioni: {results['total_transmissions']}")
        print(f"   - Tempo totale TX: {results['total_tx_time']:.2f}s")
        print(f"   - Portanti aperte: {results['carrier_openings']}")
        print(f"   - Toni CTCSS: {len(results['ctcss_tones'])}")
        print(f"   - Talk Groups: {len(results['tg_stats'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore analisi log: {e}")
        return False

def test_flask_routes():
    """Test delle route Flask di base"""
    print("\n🌐 Test route Flask...")
    
    try:
        import app
        
        with app.app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Route '/' funzionante")
            else:
                print(f"❌ Route '/' errore: {response.status_code}")
                return False
            
            # Test statistics page
            response = client.get('/statistics')
            if response.status_code == 200:
                print("✅ Route '/statistics' funzionante")
            else:
                print(f"❌ Route '/statistics' errore: {response.status_code}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Errore test route: {e}")
        return False

def test_file_upload():
    """Test upload file"""
    print("\n📤 Test upload file...")
    
    try:
        import app
        
        # Crea un file temporaneo di test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("Oct 19 08:00:00 2025: Tx1: Turning the transmitter ON\n")
            tmp.write("Oct 19 08:00:05 2025: Tx1: Turning the transmitter OFF\n")
            tmp_path = tmp.name
        
        try:
            with app.app.test_client() as client:
                with open(tmp_path, 'rb') as test_file:
                    response = client.post('/upload', data={
                        'file': (test_file, 'test_log.txt')
                    })
                
                if response.status_code == 200:
                    print("✅ Upload file funzionante")
                    result = True
                else:
                    print(f"❌ Upload file errore: {response.status_code}")
                    result = False
        finally:
            # Rimuovi il file temporaneo
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
        return result
        
    except Exception as e:
        print(f"❌ Errore test upload: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 Test Suite SVXLink Statistics")
    print("=" * 40)
    
    tests = [
        ("Importazione moduli", test_basic_import),
        ("Analisi log", test_log_analysis),  
        ("Route Flask", test_flask_routes),
        ("Upload file", test_file_upload)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Eseguendo test: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSATO")
            else:
                failed += 1
                print(f"❌ {test_name} - FALLITO")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERRORE: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 RISULTATI FINALI")
    print(f"✅ Test passati: {passed}")
    print(f"❌ Test falliti: {failed}")
    print(f"📊 Totale: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 Tutti i test sono passati! L'applicazione è pronta.")
        return True
    else:
        print(f"\n⚠️ {failed} test falliti. Controlla gli errori sopra.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)