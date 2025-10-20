#!/usr/bin/env python3
"""
Script di test per verificare l'analisi del file SVXLink log
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import SVXLinkLogAnalyzer

def test_analyzer():
    """Testa l'analyzer con il file di log esistente"""
    
    # Trova il file di log
    log_file = "sample.txt"
    
    if not os.path.exists(log_file):
        print(f"❌ File {log_file} non trovato!")
        return
    
    print(f"🔍 Analizzando il file: {log_file}")
    print("=" * 50)
    
    # Crea e configura l'analyzer
    analyzer = SVXLinkLogAnalyzer()
    
    try:
        # Analizza il file
        analyzer.parse_log_file(log_file)
        stats = analyzer.get_statistics()
        
        # Mostra i risultati
        print("📊 RISULTATI ANALISI:")
        print("-" * 30)
        
        print(f"⏱️  Tempo totale trasmissione: {stats['total_transmission_time']['hours']}h {stats['total_transmission_time']['minutes']}m {stats['total_transmission_time']['seconds']}s")
        print(f"📡 Portanti aperte: {stats['carriers_opened']}")
        print(f"🎤 Trasmissioni totali: {stats['total_transmissions']}")
        print(f"⏱️  Durata media: {stats['average_duration']['formatted']}")
        print(f"⏱️  Durata minima: {stats['min_duration']['formatted']}")
        print(f"⏱️  Durata massima: {stats['max_duration']['formatted']}")
        
        # === NUOVE STATISTICHE AVANZATE ===
        print(f"\n🎵 SUBTONI CTCSS:")
        print(f"  • Rilevamenti totali: {stats['ctcss_tones']['total_detections']}")
        print(f"  • Subtoni unici: {stats['ctcss_tones']['unique_tones']}")
        if stats['ctcss_tones']['tones_detail']:
            print(f"  • Top subtoni utilizzati:")
            for tone, count in stats['ctcss_tones']['tones_detail'][:5]:
                print(f"    - {tone} Hz: {count} volte")
        
        print(f"\n📻 TALK GROUPS:")
        print(f"  • Selezioni TG totali: {stats['talk_groups']['total_selections']}")
        print(f"  • TG unici utilizzati: {stats['talk_groups']['unique_tgs']}")
        if stats['talk_groups']['tgs_detail']:
            print(f"  • Top TG utilizzati:")
            for tg, count in stats['talk_groups']['tgs_detail'][:5]:
                print(f"    - TG #{tg}: {count} volte")
        
        print(f"\n� ANALISI QSO:")
        qso = stats['qso_analysis']
        print(f"  • QSO rilevati: {qso['total_qso']}")
        print(f"  • Tempo QSO totale: {qso['qso_time']['hours']}h {qso['qso_time']['minutes']}m {qso['qso_time']['seconds']}s")
        if qso['total_qso'] > 0:
            print(f"  • Durata media QSO: {qso['qso_avg_duration']['formatted']}")
            print(f"  • QSO più breve: {qso['qso_min_duration']['formatted']}")
            print(f"  • QSO più lungo: {qso['qso_max_duration']['formatted']}")
        
        print(f"\n�📋 EVENTI RILEVATI:")
        print("-" * 30)
        for event, count in stats['events'].items():
            print(f"  {event.replace('_', ' ').title()}: {count}")
        
        print(f"\n📝 Prime 10 trasmissioni:")
        print("-" * 30)
        for i, tx in enumerate(stats['transmissions'][:10], 1):
            duration_min = int(tx['duration_seconds'] // 60)
            duration_sec = int(tx['duration_seconds'] % 60)
            print(f"  {i:2d}. {tx['start'].strftime('%H:%M:%S')} → {tx['end'].strftime('%H:%M:%S')} ({duration_min}m {duration_sec}s)")
        
        # Mostra QSO se presenti
        if qso['qso_sessions']:
            print(f"\n💬 Prime 10 QSO rilevati:")
            print("-" * 30)
            for i, qso_session in enumerate(qso['qso_sessions'][:10], 1):
                duration_min = int(qso_session['duration_seconds'] // 60)
                duration_sec = int(qso_session['duration_seconds'] % 60)
                tg = qso_session['tg']
                print(f"  {i:2d}. TG #{tg}: {qso_session['start'].strftime('%H:%M:%S')} → {qso_session['end'].strftime('%H:%M:%S')} ({duration_min}m {duration_sec}s)")
        
        print(f"\n✅ Analisi completata con successo!")
        
        # Calcola alcune statistiche aggiuntive
        total_seconds = stats['total_transmission_time']['total_seconds']
        if total_seconds > 0:
            print(f"\n📈 STATISTICHE AGGIUNTIVE:")
            print(f"  • Percentuale di tempo in trasmissione: {(total_seconds / 86400) * 100:.2f}% (su 24h)")
            print(f"  • Trasmissioni per ora: {stats['total_transmissions'] / 24:.1f}")
            
    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")

if __name__ == "__main__":
    test_analyzer()