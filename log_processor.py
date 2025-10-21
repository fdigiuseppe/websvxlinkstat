#!/usr/bin/env python3
"""
Log Processor per SVXLink Log Analyzer
Elabora automaticamente file log dalla cartella /data e salva nel database
"""

import os
import glob
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

from database import DatabaseManager, DailyLogStats, CTCSSStats, TGStats
from app import SVXLinkLogAnalyzer

class LogProcessor:
    """Processore automatico per file log SVXLink"""
    
    def __init__(self, data_dir: str = 'data', db_path: str = 'data/svxlink_stats.db'):
        self.data_dir = Path(data_dir)
        self.db_manager = DatabaseManager(db_path)
        self.analyzer = SVXLinkLogAnalyzer()
        
        # Assicura che la directory data esista
        self.data_dir.mkdir(exist_ok=True)
    
    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Estrae la data dal nome del file"""
        # Pattern per svxlink_log_YYYY-MM-DD.txt
        patterns = [
            r'svxlink_log_(\d{4}-\d{2}-\d{2})\.txt',
            r'svxlink_(\d{4}-\d{2}-\d{2})\.log',
            r'(\d{4}-\d{2}-\d{2})\.txt',
            r'(\d{4})(\d{2})(\d{2})\.txt',  # YYYYMMDD.txt
            r'log_(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                elif len(match.groups()) == 3:
                    # YYYYMMDD format
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
        
        return None
    
    def get_unprocessed_files(self) -> List[Path]:
        """Trova file non ancora processati"""
        # Pattern per file log
        log_patterns = [
            '*.txt',
            '*.log',
            'svxlink_log_*.txt',
            'svxlink_*.log'
        ]
        
        all_files = []
        for pattern in log_patterns:
            all_files.extend(self.data_dir.glob(pattern))
        
        # Filtra file già processati
        processed_dates = set(self.db_manager.get_available_dates())
        unprocessed = []
        
        for file_path in all_files:
            file_date = self.extract_date_from_filename(file_path.name)
            if file_date and file_date not in processed_dates:
                unprocessed.append(file_path)
        
        return sorted(unprocessed)
    
    def process_log_file(self, file_path: Path) -> bool:
        """Processa singolo file log e salva nel database"""
        try:
            print(f"📄 Processando {file_path.name}...")
            
            # Estrai data dal filename
            log_date = self.extract_date_from_filename(file_path.name)
            if not log_date:
                print(f"⚠️ Non riesco a estrarre data da {file_path.name}")
                return False
            
            # Leggi file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                print(f"⚠️ File vuoto: {file_path.name}")
                return False
            
            # Analizza il log
            stats = self.analyzer.analyze_log(content)
            
            # Prepara statistiche giornaliere
            daily_stats = DailyLogStats(
                date=log_date,
                filename=file_path.name,
                file_size=file_path.stat().st_size,
                total_transmissions=stats['basic']['total_transmissions'],
                total_transmission_time=int(stats['basic']['total_transmission_time']),
                avg_transmission_time=stats['basic']['avg_transmission_time'],
                max_transmission_time=stats['basic']['max_transmission_time'],
                min_transmission_time=stats['basic']['min_transmission_time'],
                total_qso=stats['qso']['total_qso'],
                total_qso_time=int(stats['qso']['total_qso_time'])
            )
            
            # Prepara statistiche CTCSS
            ctcss_stats = []
            if stats['ctcss']['ctcss_list']:
                for ctcss_freq, data in stats['ctcss']['ctcss_list']:
                    ctcss_stats.append(CTCSSStats(
                        log_date=log_date,
                        ctcss_frequency=float(ctcss_freq),
                        count=data['count'],
                        percentage=data['percentage']
                    ))
            
            # Prepara statistiche TG
            tg_stats = []
            if stats['talk_groups']['tg_list']:
                for tg_num, data in stats['talk_groups']['tg_list']:
                    # Trova durate TG se disponibili
                    tg_duration_data = None
                    if stats['talk_groups']['tg_durations']:
                        for tg_dur, dur_data in stats['talk_groups']['tg_durations']:
                            if tg_dur == tg_num:
                                tg_duration_data = dur_data
                                break
                    
                    tg_stats.append(TGStats(
                        log_date=log_date,
                        tg_number=int(tg_num),
                        transmission_count=data['count'],
                        total_duration=int(tg_duration_data['total_seconds']) if tg_duration_data else 0,
                        qso_count=tg_duration_data['qso_count'] if tg_duration_data else 0,
                        avg_duration=tg_duration_data['avg_duration'] if tg_duration_data else 0.0,
                        percentage=data['percentage']
                    ))
            
            # Salva nel database
            success = True
            success &= self.db_manager.save_daily_stats(daily_stats)
            
            if ctcss_stats:
                success &= self.db_manager.save_ctcss_stats(ctcss_stats)
            
            if tg_stats:
                success &= self.db_manager.save_tg_stats(tg_stats)
            
            if success:
                print(f"✅ {file_path.name} processato con successo")
                print(f"   📊 {daily_stats.total_transmissions} trasmissioni, "
                      f"{daily_stats.total_qso} QSO, "
                      f"{len(ctcss_stats)} CTCSS, {len(tg_stats)} TG")
            else:
                print(f"❌ Errore nel salvataggio di {file_path.name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Errore processando {file_path.name}: {e}")
            return False
    
    def process_all_files(self, force: bool = False) -> Dict[str, int]:
        """Processa tutti i file non ancora elaborati"""
        print("🔄 Cercando file da processare...")
        
        if force:
            # Se force=True, processa tutti i file nella cartella
            unprocessed_files = list(self.data_dir.glob("svxlink_log_*.txt"))
            print(f"🔧 Modalità forzata: processamento di tutti i {len(unprocessed_files)} file")
        else:
            unprocessed_files = self.get_unprocessed_files()
        
        if not unprocessed_files:
            print("✅ Nessun file nuovo da processare")
            return {'processed': 0, 'errors': 0}
        
        print(f"📁 Trovati {len(unprocessed_files)} file da processare")
        
        processed = 0
        errors = 0
        
        for file_path in unprocessed_files:
            if self.process_log_file(file_path):
                processed += 1
            else:
                errors += 1
        
        print(f"\n🎯 Elaborazione completata:")
        print(f"   ✅ Processati: {processed}")
        print(f"   ❌ Errori: {errors}")
        print(f"   📊 Totale file nel database: {len(self.db_manager.get_available_dates())}")
        
        return {'processed': processed, 'errors': errors}
    
    def process_specific_date(self, target_date: str, force: bool = False) -> bool:
        """Processa file per una data specifica"""
        print(f"🎯 Cercando file per data: {target_date}")
        
        # Cerca file che corrispondono alla data
        all_files = list(self.data_dir.glob('*.txt')) + list(self.data_dir.glob('*.log'))
        target_files = []
        
        for file_path in all_files:
            file_date = self.extract_date_from_filename(file_path.name)
            if file_date == target_date:
                target_files.append(file_path)
        
        if not target_files:
            print(f"❌ Nessun file trovato per la data {target_date}")
            return False
        
        # Controlla se già processato
        if not force and target_date in self.db_manager.get_available_dates():
            print(f"⚠️ Data {target_date} già processata. Usa force=True per riprocessare.")
            return False
        
        # Processa il file più recente per quella data
        latest_file = max(target_files, key=lambda f: f.stat().st_mtime)
        return self.process_log_file(latest_file)
    
    def cleanup_old_files(self, keep_days: int = 30):
        """Rimuove file vecchi dalla directory data"""
        cutoff_date = datetime.now().date()
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - keep_days)
        
        removed = 0
        all_files = list(self.data_dir.glob('*.txt')) + list(self.data_dir.glob('*.log'))
        
        for file_path in all_files:
            file_date_str = self.extract_date_from_filename(file_path.name)
            if file_date_str:
                try:
                    file_date = datetime.strptime(file_date_str, '%Y-%m-%d').date()
                    if file_date < cutoff_date:
                        file_path.unlink()
                        removed += 1
                        print(f"🗑️ Rimosso file vecchio: {file_path.name}")
                except ValueError:
                    continue
        
        if removed > 0:
            print(f"🧹 Rimossi {removed} file vecchi (oltre {keep_days} giorni)")
        
        return removed
    
    def get_processing_summary(self) -> Dict:
        """Ottieni riepilogo dello stato di processamento"""
        # File disponibili
        all_files = list(self.data_dir.glob('*.txt')) + list(self.data_dir.glob('*.log'))
        
        # Date processate
        processed_dates = set(self.db_manager.get_available_dates())
        
        # File non processati
        unprocessed = self.get_unprocessed_files()
        
        # Range di date
        date_range = self.db_manager.get_date_range_stats()
        
        return {
            'total_files': len(all_files),
            'processed_dates': len(processed_dates),
            'unprocessed_files': len(unprocessed),
            'date_range': date_range,
            'unprocessed_list': [f.name for f in unprocessed[:10]]  # Prime 10
        }

# Script principale
if __name__ == "__main__":
    import sys
    
    processor = LogProcessor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "process":
            # Processa tutti i file
            processor.process_all_files()
            
        elif command == "date" and len(sys.argv) > 2:
            # Processa data specifica
            target_date = sys.argv[2]
            force = len(sys.argv) > 3 and sys.argv[3] == "--force"
            processor.process_specific_date(target_date, force)
            
        elif command == "summary":
            # Mostra riepilogo
            summary = processor.get_processing_summary()
            print("📊 Riepilogo processamento:")
            print(f"   📁 File totali: {summary['total_files']}")
            print(f"   ✅ Date processate: {summary['processed_dates']}")
            print(f"   ⏳ File da processare: {summary['unprocessed_files']}")
            
            if summary['date_range']:
                print(f"   📅 Range: {summary['date_range'].get('first_date', 'N/A')} - "
                      f"{summary['date_range'].get('last_date', 'N/A')}")
            
            if summary['unprocessed_list']:
                print("   🔄 Prossimi file da processare:")
                for filename in summary['unprocessed_list']:
                    print(f"      - {filename}")
                    
        elif command == "cleanup":
            # Pulizia file vecchi
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            processor.cleanup_old_files(days)
            
        else:
            print("❓ Comando non riconosciuto")
            print("Uso: python log_processor.py [process|date YYYY-MM-DD|summary|cleanup [days]]")
    else:
        # Default: processa tutto
        print("🚀 Log Processor - Processamento automatico")
        processor.process_all_files()