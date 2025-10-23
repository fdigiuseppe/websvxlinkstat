#!/usr/bin/env python3
"""
Database models per SVXLink Log Analyzer
Gestisce SQLite database per statistiche storiche
"""

import sqlite3
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

@dataclass
class DailyLogStats:
    """Statistiche giornaliere di un log"""
    date: str
    filename: str
    file_size: int
    total_transmissions: int
    total_transmission_time: int  # secondi
    avg_transmission_time: float
    max_transmission_time: int
    min_transmission_time: int
    total_qso: int
    total_qso_time: int

@dataclass
class CTCSSStats:
    """Statistiche CTCSS per una data"""
    log_date: str
    ctcss_frequency: float
    count: int
    percentage: float

@dataclass
class TGStats:
    """Statistiche Talk Group per una data"""
    log_date: str
    tg_number: int
    transmission_count: int
    total_duration: int
    qso_count: int
    avg_duration: float
    percentage: float

@dataclass
class QSOEvent:
    """Evento QSO singolo"""
    log_date: str
    start_time: datetime
    end_time: datetime
    duration: int
    tg_number: Optional[int] = None
    ctcss_frequency: Optional[float] = None
    event_type: str = 'qso'
    details: Optional[str] = None

class DatabaseManager:
    """Gestione database SQLite per statistiche SVXLink"""
    
    def __init__(self, db_path: str = None):
        # Usa variabile d'ambiente se disponibile, altrimenti default
        if db_path is None:
            db_path = os.getenv('DATABASE_PATH', 'data/svxlink_stats.db')
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()
    
    def ensure_db_directory(self):
        """Assicura che la directory del database esista"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Ottiene connessione al database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Inizializza il database con lo schema"""
        schema_file = 'database_schema.sql'
        if not os.path.exists(schema_file):
            print(f"⚠️ Schema file {schema_file} non trovato, creo schema basic")
            self.create_basic_schema()
            return
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with self.get_connection() as conn:
            conn.executescript(schema_sql)
            conn.commit()
            print(f"✅ Database inizializzato: {self.db_path}")
    
    def create_basic_schema(self):
        """Crea schema di base se file schema non disponibile"""
        basic_schema = """
        CREATE TABLE IF NOT EXISTS daily_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            file_size INTEGER,
            total_transmissions INTEGER DEFAULT 0,
            total_transmission_time INTEGER DEFAULT 0,
            avg_transmission_time REAL DEFAULT 0,
            max_transmission_time INTEGER DEFAULT 0,
            min_transmission_time INTEGER DEFAULT 0,
            total_qso INTEGER DEFAULT 0,
            total_qso_time INTEGER DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS daily_ctcss_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL,
            ctcss_frequency REAL NOT NULL,
            count INTEGER NOT NULL,
            percentage REAL NOT NULL,
            UNIQUE(log_date, ctcss_frequency)
        );
        
        CREATE TABLE IF NOT EXISTS daily_tg_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date DATE NOT NULL,
            tg_number INTEGER NOT NULL,
            transmission_count INTEGER NOT NULL,
            total_duration INTEGER NOT NULL,
            qso_count INTEGER NOT NULL,
            avg_duration REAL NOT NULL,
            percentage REAL NOT NULL,
            UNIQUE(log_date, tg_number)
        );
        
        CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date);
        CREATE INDEX IF NOT EXISTS idx_ctcss_stats_date ON daily_ctcss_stats(log_date);
        CREATE INDEX IF NOT EXISTS idx_tg_stats_date ON daily_tg_stats(log_date);
        """
        
        with self.get_connection() as conn:
            conn.executescript(basic_schema)
            conn.commit()
    
    def save_daily_stats(self, stats: DailyLogStats) -> bool:
        """Salva statistiche giornaliere"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO daily_logs 
                    (date, filename, file_size, total_transmissions, total_transmission_time,
                     avg_transmission_time, max_transmission_time, min_transmission_time,
                     total_qso, total_qso_time, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    stats.date, stats.filename, stats.file_size,
                    stats.total_transmissions, stats.total_transmission_time,
                    stats.avg_transmission_time, stats.max_transmission_time,
                    stats.min_transmission_time, stats.total_qso, stats.total_qso_time,
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Errore salvataggio statistiche giornaliere: {e}")
            return False
    
    def save_ctcss_stats(self, ctcss_list: List[CTCSSStats]) -> bool:
        """Salva statistiche CTCSS"""
        try:
            with self.get_connection() as conn:
                # Cancella vecchie statistiche per la data
                if ctcss_list:
                    conn.execute("DELETE FROM daily_ctcss_stats WHERE log_date = ?", 
                               (ctcss_list[0].log_date,))
                
                # Inserisci nuove statistiche
                for ctcss in ctcss_list:
                    conn.execute("""
                        INSERT INTO daily_ctcss_stats 
                        (log_date, ctcss_frequency, count, percentage)
                        VALUES (?, ?, ?, ?)
                    """, (ctcss.log_date, ctcss.ctcss_frequency, ctcss.count, ctcss.percentage))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Errore salvataggio statistiche CTCSS: {e}")
            return False
    
    def save_tg_stats(self, tg_list: List[TGStats]) -> bool:
        """Salva statistiche Talk Groups"""
        try:
            with self.get_connection() as conn:
                # Cancella vecchie statistiche per la data
                if tg_list:
                    conn.execute("DELETE FROM daily_tg_stats WHERE log_date = ?", 
                               (tg_list[0].log_date,))
                
                # Inserisci nuove statistiche
                for tg in tg_list:
                    conn.execute("""
                        INSERT INTO daily_tg_stats 
                        (log_date, tg_number, transmission_count, total_duration,
                         qso_count, avg_duration, percentage)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (tg.log_date, tg.tg_number, tg.transmission_count,
                          tg.total_duration, tg.qso_count, tg.avg_duration, tg.percentage))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Errore salvataggio statistiche TG: {e}")
            return False
    
    def get_daily_stats(self, start_date: str, end_date: str) -> List[Dict]:
        """Recupera statistiche giornaliere per periodo"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM daily_logs 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """, (start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Errore recupero statistiche giornaliere: {e}")
            return []
    
    def get_monthly_aggregated_stats(self, year: int, month: int) -> Dict:
        """Recupera statistiche aggregate mensili"""
        try:
            with self.get_connection() as conn:
                # Stats aggregate del mese
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_days,
                        SUM(total_transmissions) as total_transmissions,
                        SUM(total_transmission_time) as total_time,
                        SUM(total_qso) as total_qso,
                        AVG(total_transmissions) as avg_daily_transmissions,
                        MAX(total_transmissions) as peak_transmissions,
                        MIN(total_transmissions) as min_transmissions
                    FROM daily_logs 
                    WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                """, (str(year), f"{month:02d}"))
                
                monthly_stats = dict(cursor.fetchone() or {})
                
                # Top CTCSS del mese
                cursor = conn.execute("""
                    SELECT ctcss_frequency, SUM(count) as total_count
                    FROM daily_ctcss_stats dcs
                    JOIN daily_logs dl ON dcs.log_date = dl.date
                    WHERE strftime('%Y', dl.date) = ? AND strftime('%m', dl.date) = ?
                    GROUP BY ctcss_frequency
                    ORDER BY total_count DESC
                    LIMIT 5
                """, (str(year), f"{month:02d}"))
                
                monthly_stats['top_ctcss'] = [dict(row) for row in cursor.fetchall()]
                
                # Top TG del mese
                cursor = conn.execute("""
                    SELECT tg_number, SUM(transmission_count) as total_count,
                           SUM(total_duration) as total_duration
                    FROM daily_tg_stats dts
                    JOIN daily_logs dl ON dts.log_date = dl.date
                    WHERE strftime('%Y', dl.date) = ? AND strftime('%m', dl.date) = ?
                    GROUP BY tg_number
                    ORDER BY total_count DESC
                    LIMIT 5
                """, (str(year), f"{month:02d}"))
                
                monthly_stats['top_tgs'] = [dict(row) for row in cursor.fetchall()]
                
                return monthly_stats
        except Exception as e:
            print(f"❌ Errore recupero statistiche mensili: {e}")
            return {}
    
    def get_yearly_aggregated_stats(self, year: int) -> Dict:
        """Recupera statistiche aggregate annuali"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_days,
                        SUM(total_transmissions) as total_transmissions,
                        SUM(total_transmission_time) as total_time,
                        SUM(total_qso) as total_qso,
                        AVG(total_transmissions) as avg_daily_transmissions,
                        MAX(total_transmissions) as peak_transmissions,
                        MIN(total_transmissions) as min_transmissions
                    FROM daily_logs 
                    WHERE strftime('%Y', date) = ?
                """, (str(year),))
                
                return dict(cursor.fetchone() or {})
        except Exception as e:
            print(f"❌ Errore recupero statistiche annuali: {e}")
            return {}
    
    def get_available_dates(self) -> List[str]:
        """Recupera tutte le date disponibili nel database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT DISTINCT date FROM daily_logs ORDER BY date DESC")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Errore recupero date disponibili: {e}")
            return []
    
    def get_date_range_stats(self) -> Dict:
        """Recupera statistiche sul range di date disponibili"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        MIN(date) as first_date,
                        MAX(date) as last_date,
                        COUNT(*) as total_days
                    FROM daily_logs
                """)
                
                return dict(cursor.fetchone() or {})
        except Exception as e:
            print(f"❌ Errore recupero range date: {e}")
            return {}
    
    def cleanup_old_data(self, keep_days: int = 365):
        """Pulisce dati vecchi mantenendo solo gli ultimi N giorni"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM daily_logs 
                    WHERE date < date('now', '-{} days')
                """.format(keep_days))
                
                deleted = cursor.rowcount
                conn.commit()
                
                if deleted > 0:
                    print(f"🧹 Eliminati {deleted} record vecchi (oltre {keep_days} giorni)")
                
                return deleted
        except Exception as e:
            print(f"❌ Errore pulizia dati: {e}")
            return 0
    
    def reset_database(self):
        """Resetta completamente il database eliminando tutti i dati e ricreando le tabelle"""
        try:
            with self.get_connection() as conn:
                # Conta i record prima della cancellazione per logging
                cursor = conn.execute("SELECT COUNT(*) as count FROM daily_logs")
                count_before = cursor.fetchone()['count']
                
                # Elimina tutte le tabelle
                tables = ['daily_logs', 'ctcss_stats', 'tg_stats', 'qso_events', 'transmissions']
                for table in tables:
                    try:
                        conn.execute(f"DROP TABLE IF EXISTS {table}")
                        print(f"🗑️ Tabella {table} eliminata")
                    except Exception as e:
                        print(f"⚠️ Errore eliminazione tabella {table}: {e}")
                
                conn.commit()
                print(f"🧹 Database resettato: eliminati {count_before} record")
                
                # Ricrea lo schema
                self.init_database()
                print("✅ Schema database ricreato")
                
                return count_before
                
        except Exception as e:
            print(f"❌ Errore reset database: {e}")
            raise e
    
    def get_ctcss_stats(self, start_date: str, end_date: str) -> List[Dict]:
        """Recupera statistiche CTCSS aggregate per range di date"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        ctcss_frequency,
                        SUM(count) as total_count,
                        AVG(percentage) as avg_percentage
                    FROM daily_ctcss_stats
                    WHERE log_date BETWEEN ? AND ?
                    GROUP BY ctcss_frequency
                    ORDER BY total_count DESC
                """, (start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Errore recupero statistiche CTCSS: {e}")
            return []
    
    def get_tg_stats(self, start_date: str, end_date: str) -> List[Dict]:
        """Recupera statistiche Talk Group aggregate per range di date"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        tg_number,
                        SUM(transmission_count) as total_transmissions,
                        SUM(total_duration) as total_duration,
                        SUM(qso_count) as total_qso,
                        AVG(avg_duration) as avg_duration,
                        AVG(percentage) as avg_percentage
                    FROM daily_tg_stats
                    WHERE log_date BETWEEN ? AND ? AND tg_number != 0
                    GROUP BY tg_number
                    ORDER BY total_transmissions DESC
                """, (start_date, end_date))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Errore recupero statistiche TG: {e}")
            return []
    
    def get_all_daily_stats(self):
        """Recupera tutte le statistiche giornaliere (per conteggio record)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM daily_logs ORDER BY date DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"❌ Errore recupero tutti i dati: {e}")
            return []

# Test del database manager
if __name__ == "__main__":
    print("🧪 Test Database Manager...")
    
    db = DatabaseManager('test_stats.db')
    
    # Test salvataggio dati
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
        print("✅ Test salvataggio riuscito")
    
    # Test recupero dati
    stats = db.get_daily_stats("2025-10-21", "2025-10-21")
    if stats:
        print(f"✅ Test recupero riuscito: {len(stats)} record")
    
    # Test range date
    date_range = db.get_date_range_stats()
    print(f"📅 Range date: {date_range}")
    
    print("🎉 Test completati!")