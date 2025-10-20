#!/usr/bin/env python3
"""
Test script per verificare il calcolo delle durate dei Talk Groups
"""

from app import SVXLinkLogAnalyzer

def test_tg_analysis():
    analyzer = SVXLinkLogAnalyzer()
    
    # Analizza il file di esempio
    with open('sample.txt', 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    # Esegui l'analisi
    stats = analyzer.analyze_log(content)
    
    print("=== ANALISI TALK GROUPS ===")
    print(f"Talk Groups rilevati: {stats['talk_groups']['total_tg']}")
    print(f"QSO con TG: {stats['talk_groups']['qso_with_tg']}")
    
    print("\n=== DISTRIBUZIONE TALK GROUPS ===")
    for tg, data in stats['talk_groups']['tg_list']:
        print(f"TG #{tg}: {data['count']} trasmissioni ({data['percentage']:.1f}%)")
    
    print("\n=== DURATE TALK GROUPS ===")
    if stats['talk_groups']['tg_durations']:
        for tg, data in stats['talk_groups']['tg_durations']:
            minutes = int(data['total_seconds'] // 60)
            seconds = int(data['total_seconds'] % 60)
            avg_min = int(data['avg_duration'] // 60)
            avg_sec = int(data['avg_duration'] % 60)
            print(f"TG #{tg}:")
            print(f"  - Durata totale: {minutes}m {seconds}s")
            print(f"  - QSO rilevati: {data['qso_count']}")
            print(f"  - Durata media QSO: {avg_min}m {avg_sec}s")
            print()
    else:
        print("Nessun TG con QSO rilevato")

if __name__ == "__main__":
    test_tg_analysis()