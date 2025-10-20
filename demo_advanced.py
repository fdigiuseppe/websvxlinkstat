#!/usr/bin/env python3
"""
Demo delle nuove funzionalità avanzate dell'SVXLink Log Analyzer
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import SVXLinkLogAnalyzer

def demo_advanced_features():
    """Dimostra le nuove funzionalità implementate"""
    
    print("🚀 SVXLink Log Analyzer - FUNZIONALITÀ AVANZATE")
    print("=" * 60)
    
    # Crea analyzer
    analyzer = SVXLinkLogAnalyzer()
    
    try:
        # Analizza il file
        analyzer.parse_log_file("sample.txt")
        stats = analyzer.get_statistics()
        
        print("📊 PANORAMICA GENERALE:")
        print(f"   • File analizzato: sample.txt")
        print(f"   • Tempo trasmissione: {stats['total_transmission_time']['hours']}h {stats['total_transmission_time']['minutes']}m {stats['total_transmission_time']['seconds']}s")
        print(f"   • Portanti aperte: {stats['carriers_opened']}")
        print(f"   • Trasmissioni totali: {stats['total_transmissions']}")
        
        print(f"\n🎵 ANALISI SUBTONI CTCSS:")
        print(f"   • Subtoni unici rilevati: {stats['ctcss_tones']['unique_tones']}")
        print(f"   • Rilevamenti totali: {stats['ctcss_tones']['total_detections']}")
        print(f"   • Top 3 subtoni più utilizzati:")
        for i, (tone, count) in enumerate(stats['ctcss_tones']['tones_detail'][:3], 1):
            percentage = (count / stats['ctcss_tones']['total_detections']) * 100
            print(f"     {i}. {tone} Hz - {count} volte ({percentage:.1f}%)")
        
        print(f"\n📻 ANALISI TALK GROUPS:")
        print(f"   • TG unici utilizzati: {stats['talk_groups']['unique_tgs']}")
        print(f"   • Selezioni TG totali: {stats['talk_groups']['total_selections']}")
        print(f"   • Top 3 TG più utilizzati:")
        for i, (tg, count) in enumerate(stats['talk_groups']['tgs_detail'][:3], 1):
            percentage = (count / stats['talk_groups']['total_selections']) * 100
            print(f"     {i}. TG #{tg} - {count} volte ({percentage:.1f}%)")
        
        print(f"\n💬 ANALISI QSO AVANZATA:")
        qso = stats['qso_analysis']
        print(f"   • QSO completi rilevati: {qso['total_qso']}")
        print(f"   • Tempo QSO totale: {qso['qso_time']['hours']}h {qso['qso_time']['minutes']}m {qso['qso_time']['seconds']}s")
        print(f"   • Durata media QSO: {qso['qso_avg_duration']['formatted']}")
        print(f"   • QSO più lungo: {qso['qso_max_duration']['formatted']}")
        print(f"   • QSO più breve: {qso['qso_min_duration']['formatted']}")
        
        # Mostra distribuzione QSO per TG
        if qso['qso_sessions']:
            tg_distribution = {}
            for qso_session in qso['qso_sessions']:
                tg = qso_session['tg']
                tg_distribution[tg] = tg_distribution.get(tg, 0) + 1
            
            print(f"   • Distribuzione QSO per TG:")
            sorted_tg_dist = sorted(tg_distribution.items(), key=lambda x: x[1], reverse=True)
            for tg, count in sorted_tg_dist:
                percentage = (count / qso['total_qso']) * 100
                print(f"     - TG #{tg}: {count} QSO ({percentage:.1f}%)")
        
        print(f"\n🔍 PATTERN IDENTIFICATI:")
        
        # Calcola alcune statistiche interessanti
        total_seconds_day = 24 * 60 * 60
        tx_percentage = (stats['total_transmission_time']['total_seconds'] / total_seconds_day) * 100
        qso_percentage = (qso['qso_time']['total_seconds'] / stats['total_transmission_time']['total_seconds']) * 100 if stats['total_transmission_time']['total_seconds'] > 0 else 0
        
        print(f"   • Utilizzo ponte: {tx_percentage:.2f}% del tempo totale")
        print(f"   • QSO vs TX totale: {qso_percentage:.1f}% del tempo trasmissione")
        print(f"   • Media TX per ora: {stats['total_transmissions'] / 24:.1f}")
        print(f"   • Media QSO per ora: {qso['total_qso'] / 24:.1f}")
        
        # Analizza i subtoni più comuni
        if stats['ctcss_tones']['tones_detail']:
            most_used_tone = stats['ctcss_tones']['tones_detail'][0]
            tone_dominance = (most_used_tone[1] / stats['ctcss_tones']['total_detections']) * 100
            print(f"   • Subtono dominante: {most_used_tone[0]} Hz ({tone_dominance:.1f}% dei rilevamenti)")
        
        # Analizza i TG più attivi
        if stats['talk_groups']['tgs_detail']:
            most_used_tg = stats['talk_groups']['tgs_detail'][0]
            tg_dominance = (most_used_tg[1] / stats['talk_groups']['total_selections']) * 100
            print(f"   • TG più attivo: TG #{most_used_tg[0]} ({tg_dominance:.1f}% delle selezioni)")
        
        print(f"\n✅ Analisi avanzata completata!")
        print(f"\n🌐 Puoi vedere tutti i dettagli nell'interfaccia web su:")
        print(f"   http://127.0.0.1:5000")
        
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    demo_advanced_features()