#!/usr/bin/env python3
"""
Test script indipendente per verificare il calcolo delle durate dei Talk Groups
"""
import re
from datetime import datetime
from collections import defaultdict

class TGAnalyzer:
    def __init__(self):
        self.qso_patterns = [
            r'DTMF.*[*#]',
            r'TG #\d+.*activating',
            r'TG #\d+.*deactivating'
        ]
    
    def analyze_tg_durations(self, content):
        lines = content.strip().split('\n')
        
        # Trova tutti gli eventi "Talker start" e "Talker stop"
        talker_events = []
        for line in lines:
            if 'Talker start on TG' in line or 'Talker stop on TG' in line:
                print(f"Linea trovata: {line}")
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    print(f"Timestamp trovato: {timestamp_match.group(1)}")
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    talker_events.append((timestamp, line))
                else:
                    print(f"Timestamp NON trovato in: {line}")
        
        print(f"Trovati {len(talker_events)} eventi talker")
        
        # Test: prendi solo i primi 10 per non intasare
        if len(talker_events) > 10:
            print("(Limitando a primi 10 eventi per debug)")
            talker_events = talker_events[:10]
        
        # Calcola durate per TG basandosi su start/stop
        tg_durations = defaultdict(lambda: {'total_seconds': 0, 'qso_count': 0})
        
        i = 0
        while i < len(talker_events):
            _, line = talker_events[i]
            
            if 'Talker start on TG' in line:
                # Trova il TG
                tg_match = re.search(r'TG #(\d+)', line)
                if tg_match:
                    tg = tg_match.group(1)
                    start_time = talker_events[i][0]
                    
                    print(f"Start trovato per TG #{tg} alle {start_time}")
                    
                    # Cerca il corrispondente "stop"
                    for j in range(i + 1, len(talker_events)):
                        _, stop_line = talker_events[j]
                        if 'Talker stop on TG' in stop_line and f'TG #{tg}' in stop_line:
                            stop_time = talker_events[j][0]
                            duration = (stop_time - start_time).total_seconds()
                            
                            print(f"Stop trovato per TG #{tg} alle {stop_time}, durata: {duration}s")
                            
                            tg_durations[tg]['total_seconds'] += duration
                            tg_durations[tg]['qso_count'] += 1
                            break
            i += 1
        
        # Calcola durata media
        for tg in tg_durations:
            count = tg_durations[tg]['qso_count']
            if count > 0:
                tg_durations[tg]['avg_duration'] = tg_durations[tg]['total_seconds'] / count
        
        # Ordina per durata totale
        sorted_tg = sorted(tg_durations.items(), key=lambda x: x[1]['total_seconds'], reverse=True)
        
        return sorted_tg

def test_tg_analysis():
    analyzer = TGAnalyzer()
    
    # Leggi il file di esempio
    print("Leggendo il file sample.txt...")
    with open('sample.txt', 'r', encoding='utf-8', errors='ignore') as file:
        content = file.read()
    
    print(f"File letto, lunghezza: {len(content)} caratteri")
    
    # Controlla se ci sono linee con "Talker"
    lines = content.split('\n')
    talker_lines = [line for line in lines if 'Talker' in line]
    print(f"Linee con 'Talker': {len(talker_lines)}")
    
    if talker_lines:
        print("Prime 5 linee con Talker:")
        for line in talker_lines[:5]:
            print(f"  {line}")
    
    # Analizza le durate TG
    tg_durations = analyzer.analyze_tg_durations(content)
    
    print("\n=== DURATE TALK GROUPS ===")
    if tg_durations:
        for tg, data in tg_durations:
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