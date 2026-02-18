#!/usr/bin/env python3
"""Test script per verificare il tracciamento delle disconnessioni"""

from app import SVXLinkLogAnalyzer

def test_disconnections():
    analyzer = SVXLinkLogAnalyzer()
    
    # Test file con disconnessioni consecutive (febbraio 2026)
    print("=" * 60)
    print("Test 1: File con disconnessioni consecutive")
    print("=" * 60)
    
    with open('data/svxlink_log_2026-02-17.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    stats = analyzer.analyze_log(content)
    disc = stats['disconnections']
    
    print(f"Periodi di disconnessione: {disc['total_periods']}")
    print(f"Totale disconnessioni: {disc['total_disconnections']}")
    
    if disc['periods']:
        for i, period in enumerate(disc['periods'], 1):
            print(f"\nPeriodo {i}:")
            print(f"  - Inizio: {period['start']}")
            print(f"  - Fine: {period.get('end', 'N/A')}")
            print(f"  - Durata: {period.get('duration_formatted', 'N/A')}")
            print(f"  - N° disconnessioni: {period.get('count', 0)}")
            print(f"  - Stato: {period.get('status', 'unknown')}")
    
    # Test file con eventi Node joined/left (ottobre 2025)
    print("\n" + "=" * 60)
    print("Test 2: File con eventi di riconnessione")
    print("=" * 60)
    
    analyzer2 = SVXLinkLogAnalyzer()
    
    with open('data/svxlink_log_2025-10-21.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    stats2 = analyzer2.analyze_log(content)
    disc2 = stats2['disconnections']
    
    print(f"Periodi di disconnessione: {disc2['total_periods']}")
    print(f"Totale disconnessioni: {disc2['total_disconnections']}")
    
    if disc2['periods']:
        for i, period in enumerate(disc2['periods'], 1):
            print(f"\nPeriodo {i}:")
            print(f"  - Inizio: {period['start']}")
            print(f"  - Fine: {period.get('end', 'N/A')}")
            print(f"  - Durata: {period.get('duration_formatted', 'N/A')}")
            print(f"  - N° disconnessioni: {period.get('count', 0)}")
            print(f"  - Stato: {period.get('status', 'unknown')}")
    else:
        print("\nNessuna disconnessione trovata in questo file")
    
    print("\n" + "=" * 60)
    print("Test completati!")
    print("=" * 60)

if __name__ == "__main__":
    test_disconnections()
