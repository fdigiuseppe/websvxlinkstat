#!/usr/bin/env python3
"""
Scheduler per processamento automatico file log SVXLink
Esegue il processamento dei nuovi file ogni giorno alle 00:01
"""

import threading
import time
import schedule
import logging
from datetime import datetime
from log_processor import LogProcessor

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/scheduler.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)

class LogScheduler:
    """Scheduler per processamento automatico dei log"""
    
    def __init__(self):
        self.processor = LogProcessor()
        self.running = False
        self.thread = None
    
    def process_daily_logs(self):
        """Job giornaliero per processare nuovi file"""
        try:
            logger.info("🔄 Avvio processamento automatico giornaliero")
            
            # Processa tutti i file non elaborati
            result = self.processor.process_all_files()
            
            logger.info(f"✅ Processamento completato: {result['processed']} file processati, {result['errors']} errori")
            
            # Pulizia file vecchi (opzionale, mantieni ultimi 60 giorni)
            if result['processed'] > 0:
                cleaned = self.processor.cleanup_old_files(keep_days=60)
                if cleaned > 0:
                    logger.info(f"🧹 Puliti {cleaned} file vecchi")
            
            # Pulizia database (mantieni ultimi 2 anni)
            cleaned_db = self.processor.db_manager.cleanup_old_data(keep_days=730)
            if cleaned_db > 0:
                logger.info(f"🗄️ Puliti {cleaned_db} record vecchi dal database")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Errore nel processamento automatico: {e}")
            return {'processed': 0, 'errors': 1}
    
    def process_on_startup(self):
        """Processa file all'avvio dell'applicazione"""
        try:
            logger.info("🚀 Processamento file all'avvio...")
            
            # Controlla se ci sono file non processati
            summary = self.processor.get_processing_summary()
            
            if summary['unprocessed_files'] > 0:
                logger.info(f"📁 Trovati {summary['unprocessed_files']} file non processati")
                result = self.processor.process_all_files()
                logger.info(f"✅ Processamento avvio completato: {result['processed']} file processati")
                return result
            else:
                logger.info("✨ Nessun file da processare all'avvio")
                return {'processed': 0, 'errors': 0}
                
        except Exception as e:
            logger.error(f"❌ Errore processamento avvio: {e}")
            return {'processed': 0, 'errors': 1}
    
    def start_scheduler(self):
        """Avvia lo scheduler in background"""
        if self.running:
            logger.warning("⚠️ Scheduler già in esecuzione")
            return
        
        # Configura i job schedulati
        schedule.clear()
        
        # Job giornaliero alle 00:01
        schedule.every().day.at("00:01").do(self.process_daily_logs)
        
        # Job opzionale ogni 6 ore per controllo file nuovi
        schedule.every(6).hours.do(self._check_new_files)
        
        self.running = True
        
        # Avvia il thread dello scheduler
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        
        logger.info("⏰ Scheduler avviato - processamento giornaliero alle 00:01")
        
        # Processa file all'avvio
        threading.Thread(target=self.process_on_startup, daemon=True).start()
    
    def stop_scheduler(self):
        """Ferma lo scheduler"""
        if not self.running:
            return
        
        self.running = False
        schedule.clear()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logger.info("🛑 Scheduler fermato")
    
    def _run_scheduler(self):
        """Loop principale dello scheduler"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Controlla ogni minuto
            except Exception as e:
                logger.error(f"❌ Errore nel loop scheduler: {e}")
                time.sleep(60)
    
    def _check_new_files(self):
        """Controlla se ci sono nuovi file da processare (job ogni 6 ore)"""
        try:
            summary = self.processor.get_processing_summary()
            
            if summary['unprocessed_files'] > 0:
                logger.info(f"🔍 Controllo periodico: trovati {summary['unprocessed_files']} file non processati")
                
                # Processa solo se ci sono più di 2 file in attesa
                if summary['unprocessed_files'] >= 2:
                    result = self.processor.process_all_files()
                    logger.info(f"⚡ Processamento periodico: {result['processed']} file processati")
            else:
                logger.debug("✨ Controllo periodico: nessun file da processare")
                
        except Exception as e:
            logger.error(f"❌ Errore controllo periodico: {e}")
    
    def get_next_runs(self):
        """Ottieni prossimi job schedulati"""
        try:
            jobs = []
            for job in schedule.jobs:
                jobs.append({
                    'job': str(job.job_func.__name__),
                    'next_run': job.next_run.isoformat() if job.next_run else None,
                    'interval': str(job.interval)
                })
            return jobs
        except Exception as e:
            logger.error(f"❌ Errore recupero job: {e}")
            return []
    
    def force_process(self):
        """Forza processamento immediato"""
        logger.info("🔨 Processamento forzato richiesto")
        return self.process_daily_logs()

# Istanza globale dello scheduler
scheduler_instance = None

def get_scheduler():
    """Ottieni l'istanza dello scheduler"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = LogScheduler()
    return scheduler_instance

def init_scheduler():
    """Inizializza e avvia lo scheduler"""
    scheduler = get_scheduler()
    scheduler.start_scheduler()
    return scheduler

def stop_scheduler():
    """Ferma lo scheduler"""
    global scheduler_instance
    if scheduler_instance:
        scheduler_instance.stop_scheduler()
        scheduler_instance = None

# Test dello scheduler
if __name__ == "__main__":
    print("🧪 Test Log Scheduler...")
    
    # Crea scheduler
    scheduler = LogScheduler()
    
    try:
        # Test processamento
        result = scheduler.process_on_startup()
        print(f"✅ Test processamento: {result}")
        
        # Test scheduler (breve)
        print("⏰ Test scheduler per 10 secondi...")
        scheduler.start_scheduler()
        
        time.sleep(10)
        
        # Mostra prossimi job
        jobs = scheduler.get_next_runs()
        print(f"📅 Job schedulati: {jobs}")
        
    finally:
        scheduler.stop_scheduler()
        print("🎉 Test completato!")