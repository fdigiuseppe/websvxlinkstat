#!/usr/bin/env python3
"""Script per verificare i dati nel database"""

from database import DatabaseManager

db = DatabaseManager()

# Verifica statistiche giornaliere
stats = db.get_daily_stats('2026-02-17', '2026-02-17')
print(f'Statistiche giornaliere: {len(stats)} giorni trovati')
for s in stats:
    print(f'  Data: {s["date"]}')
    print(f'  Trasmissioni: {s["total_transmissions"]}')
    print(f'  QSO: {s["total_qso"]}')
    print(f'  Tempo totale: {s["total_transmission_time"]}s')

# Verifica disconnessioni
print('\n--- Disconnessioni ---')
disconn = db.get_disconnections('2026-02-17', '2026-02-17')
print(f'Periodi di disconnessione: {len(disconn)}')
for d in disconn:
    print(f'  Data: {d["log_date"]}')
    print(f'  Inizio: {d["start_time"]}')
    print(f'  Fine: {d["end_time"]}')
    print(f'  Durata: {d["duration"]}')
    print(f'  Conteggio: {d["disconnection_count"]}')
    print(f'  Status: {d["status"]}')
