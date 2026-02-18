#!/usr/bin/env python3
"""
SVXLink Log Analyzer - Web Application

Questa applicazione analizza i file di log SVXLink per determinare:
- Tempo totale di utilizzo del ponte per trasmissione (QSO)
- Numero di portanti aperte
- Statistiche dettagliate delle trasmissioni
"""

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from datetime import datetime, timedelta, date
import re
from collections import defaultdict
import tempfile

# Import per database e statistiche - importazione differita per evitare cicli
try:
    from database import DatabaseManager
    # LogProcessor sarà importato dopo la definizione della classe SVXLinkLogAnalyzer
    DB_AVAILABLE = True
except ImportError:
    print("⚠️ Database modules non disponibili. Funzionalità statistiche limitate.")
    DB_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'svxlink_analyzer_secret_key_2024'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configurazione per reverse proxy Apache con HTTPS
app.config['APPLICATION_ROOT'] = '/websvxlinkstat'
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SERVER_NAME'] = None  # Lascia che Flask si adatti all'host

# Configura ProxyFix per gestire headers del reverse proxy
app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_prefix=1
)

# Le inizializzazioni di log_processor e scheduler saranno fatte dopo 
# la definizione della classe SVXLinkLogAnalyzer per evitare importazioni circolari

# Inizializza variabili globali
db_manager = None
log_processor = None  
scheduler = None

class SVXLinkLogAnalyzer:
    def __init__(self):
        self.transmissions = []
        self.carriers_opened = 0
        self.total_transmission_time = timedelta()
        self.stats = defaultdict(int)
        # Nuove statistiche avanzate
        self.ctcss_tones = defaultdict(int)  # Subtoni rilevati per frequenza
        self.talk_groups = defaultdict(int)  # TG aperti con conteggio
        self.qso_sessions = []  # QSO completi identificati
        self.active_tg = None  # TG attualmente attivo
        self.qso_start = None  # Inizio QSO corrente
        # Tracciamento disconnessioni
        self.disconnections = []  # Periodi di disconnessione
        self.current_disconnection = None  # Disconnessione attualmente in corso
        
    def parse_log_file(self, file_path):
        """Analizza il file di log SVXLink"""
        self.transmissions = []
        self.carriers_opened = 0
        self.total_transmission_time = timedelta()
        self.stats = defaultdict(int)
        # Reset delle nuove statistiche
        self.ctcss_tones = defaultdict(int)
        self.talk_groups = defaultdict(int)
        self.qso_sessions = []
        self.active_tg = None
        self.qso_start = None
        # Reset disconnessioni
        self.disconnections = []
        self.current_disconnection = None
        
        tx_sessions = []  # Per tracciare le sessioni ON/OFF
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse del timestamp e del messaggio
                # Supporta sia "Oct 21" che "Nov  1" (con spazio extra per giorni a cifra singola)
                match = re.match(r'^(\w{3} \w{3} \s*\d{1,2} \d{2}:\d{2}:\d{2} \d{4}): (.+)$', line)
                if not match:
                    continue
                    
                timestamp_str, message = match.groups()
                # Normalizza gli spazi extra nel timestamp prima del parsing
                timestamp_str = re.sub(r'\s+', ' ', timestamp_str.strip())
                timestamp = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Y')
                
                # === ANALISI SUBTONI CTCSS ===
                ctcss_match = re.search(r'(\d+\.?\d*) Hz CTCSS tone detected', message)
                if ctcss_match:
                    tone_freq = float(ctcss_match.group(1))
                    self.ctcss_tones[tone_freq] += 1
                    self.stats['ctcss_detections'] += 1
                    
                    # Possibile inizio QSO se c'è un subtono
                    if self.qso_start is None:
                        self.qso_start = timestamp
                
                # === ANALISI TALK GROUPS ===
                tg_match = re.search(r'Selecting TG #(\d+)', message)
                if tg_match:
                    tg_number = int(tg_match.group(1))
                    
                    # Se TG #0, potrebbe essere fine QSO
                    if tg_number == 0:
                        if self.active_tg is not None and self.qso_start is not None:
                            # Registra QSO completo
                            qso_duration = timestamp - self.qso_start
                            self.qso_sessions.append({
                                'start': self.qso_start,
                                'end': timestamp,
                                'duration': qso_duration,
                                'tg': self.active_tg,
                                'duration_seconds': qso_duration.total_seconds()
                            })
                        self.active_tg = None
                        self.qso_start = None
                    else:
                        # TG diverso da 0 - possibile inizio/cambio QSO
                        self.talk_groups[tg_number] += 1
                        self.active_tg = tg_number
                        
                        # Se non abbiamo un inizio QSO, lo impostiamo ora
                        if self.qso_start is None:
                            self.qso_start = timestamp
                
                # Cerca eventi di trasmissione
                if "Turning the transmitter ON" in message:
                    # Nuova trasmissione inizia
                    tx_sessions.append({
                        'start': timestamp,
                        'end': None,
                        'message': message
                    })
                    self.carriers_opened += 1
                    self.stats['transmitter_on'] += 1
                    
                elif "Turning the transmitter OFF" in message:
                    # Trasmissione termina
                    if tx_sessions and tx_sessions[-1]['end'] is None:
                        tx_sessions[-1]['end'] = timestamp
                        
                        # Calcola durata
                        duration = timestamp - tx_sessions[-1]['start']
                        self.total_transmission_time += duration
                        
                        self.transmissions.append({
                            'start': tx_sessions[-1]['start'],
                            'end': timestamp,
                            'duration': duration,
                            'duration_seconds': duration.total_seconds()
                        })
                        
                    self.stats['transmitter_off'] += 1
                
                # Altri eventi interessanti
                elif "squelch is OPEN" in message:
                    self.stats['squelch_open'] += 1
                elif "squelch is CLOSED" in message:
                    self.stats['squelch_closed'] += 1
                elif "Talker start" in message:
                    self.stats['talker_start'] += 1
                elif "Talker stop" in message:
                    self.stats['talker_stop'] += 1
                elif "Node joined" in message or "Node left" in message:
                    # Eventi di nodi - chiudono eventuali disconnessioni in corso
                    if self.current_disconnection:
                        self.current_disconnection['end'] = timestamp
                        self.current_disconnection['duration'] = (timestamp - self.current_disconnection['start']).total_seconds()
                        self.disconnections.append(self.current_disconnection)
                        self.current_disconnection = None
                    
                    if "Node joined" in message:
                        self.stats['nodes_joined'] += 1
                    else:
                        self.stats['nodes_left'] += 1
                elif "identification" in message.lower():
                    self.stats['identifications'] += 1
                
                # === TRACCIAMENTO DISCONNESSIONI ===
                if "ReflectorLogic: Disconnected from" in message and "Connection timed out" in message:
                    if self.current_disconnection is None:
                        # Inizio nuovo periodo di disconnessione
                        self.current_disconnection = {
                            'start': timestamp,
                            'end': None,
                            'count': 1,
                            'last_disconnection': timestamp
                        }
                    else:
                        # Incrementa il contatore di disconnessioni dello stesso periodo
                        self.current_disconnection['count'] += 1
                        self.current_disconnection['last_disconnection'] = timestamp
                    self.stats['disconnections'] += 1
            
            # Gestione disconnessioni ancora in corso alla fine del log
            if self.current_disconnection:
                # Chiudi il periodo con l'ultima disconnessione rilevata
                self.current_disconnection['end'] = self.current_disconnection['last_disconnection']
                self.current_disconnection['duration'] = (
                    self.current_disconnection['last_disconnection'] - 
                    self.current_disconnection['start']
                ).total_seconds()
                self.current_disconnection['status'] = 'resolved'
                self.disconnections.append(self.current_disconnection)
                self.current_disconnection = None
                    
        except Exception as e:
            raise Exception(f"Errore durante l'analisi del file: {str(e)}")
    
    def get_statistics(self):
        """Restituisce le statistiche calcolate"""
        total_seconds = self.total_transmission_time.total_seconds()
        
        # Calcola statistiche di durata
        durations = [t['duration_seconds'] for t in self.transmissions]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Calcola statistiche QSO
        qso_durations = [q['duration_seconds'] for q in self.qso_sessions]
        qso_total_time = sum(qso_durations)
        qso_avg_duration = sum(qso_durations) / len(qso_durations) if qso_durations else 0
        qso_min_duration = min(qso_durations) if qso_durations else 0
        qso_max_duration = max(qso_durations) if qso_durations else 0
        
        # Prepara i subtoni per il display (ordinati per frequenza di utilizzo)
        sorted_ctcss = sorted(self.ctcss_tones.items(), key=lambda x: x[1], reverse=True)
        
        # Prepara i TG per il display (ordinati per frequenza di utilizzo)
        sorted_tg = sorted(self.talk_groups.items(), key=lambda x: x[1], reverse=True)
        
        # Calcola durate per Talk Group
        tg_durations = {}
        for qso_session in self.qso_sessions:
            tg = qso_session['tg']
            if tg not in tg_durations:
                tg_durations[tg] = {
                    'total_seconds': 0,
                    'qso_count': 0,
                    'avg_duration': 0
                }
            tg_durations[tg]['total_seconds'] += qso_session['duration_seconds']
            tg_durations[tg]['qso_count'] += 1
        
        # Calcola durate medie per TG
        for tg in tg_durations:
            avg_seconds = tg_durations[tg]['total_seconds'] / tg_durations[tg]['qso_count']
            tg_durations[tg]['avg_duration'] = avg_seconds
            tg_durations[tg]['formatted_total'] = f"{int(tg_durations[tg]['total_seconds'] // 60)}m {int(tg_durations[tg]['total_seconds'] % 60)}s"
            tg_durations[tg]['formatted_avg'] = f"{int(avg_seconds // 60)}m {int(avg_seconds % 60)}s"
        
        # Ordina TG per durata totale (decrescente)
        sorted_tg_by_duration = sorted(tg_durations.items(), key=lambda x: x[1]['total_seconds'], reverse=True)
        
        return {
            'total_transmission_time': {
                'hours': int(total_seconds // 3600),
                'minutes': int((total_seconds % 3600) // 60),
                'seconds': int(total_seconds % 60),
                'total_seconds': total_seconds
            },
            'carriers_opened': self.carriers_opened,
            'total_transmissions': len(self.transmissions),
            'average_duration': {
                'seconds': avg_duration,
                'formatted': f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s"
            },
            'min_duration': {
                'seconds': min_duration,
                'formatted': f"{int(min_duration // 60)}m {int(min_duration % 60)}s"
            },
            'max_duration': {
                'seconds': max_duration,
                'formatted': f"{int(max_duration // 60)}m {int(max_duration % 60)}s"
            },
            # === NUOVE STATISTICHE AVANZATE ===
            'ctcss_tones': {
                'total_detections': sum(self.ctcss_tones.values()),
                'unique_tones': len(self.ctcss_tones),
                'tones_detail': sorted_ctcss[:10]  # Top 10 subtoni più usati
            },
            'talk_groups': {
                'total_selections': sum(self.talk_groups.values()),
                'unique_tgs': len(self.talk_groups),
                'tgs_detail': sorted_tg[:10],  # Top 10 TG più usati
                'tg_durations': sorted_tg_by_duration  # TG ordinati per durata totale
            },
            'qso_analysis': {
                'total_qso': len(self.qso_sessions),
                'qso_time': {
                    'hours': int(qso_total_time // 3600),
                    'minutes': int((qso_total_time % 3600) // 60),
                    'seconds': int(qso_total_time % 60),
                    'total_seconds': qso_total_time
                },
                'qso_avg_duration': {
                    'seconds': qso_avg_duration,
                    'formatted': f"{int(qso_avg_duration // 60)}m {int(qso_avg_duration % 60)}s"
                },
                'qso_min_duration': {
                    'seconds': qso_min_duration,
                    'formatted': f"{int(qso_min_duration // 60)}m {int(qso_min_duration % 60)}s"
                },
                'qso_max_duration': {
                    'seconds': qso_max_duration,
                    'formatted': f"{int(qso_max_duration // 60)}m {int(qso_max_duration % 60)}s"
                },
                'qso_sessions': self.qso_sessions[:20]  # Prime 20 QSO per performance
            },
            'disconnections': {
                'total_periods': len(self.disconnections),
                'total_disconnections': sum(d['count'] for d in self.disconnections),
                'periods': [
                    {
                        'start': d['start'].strftime('%Y-%m-%d %H:%M:%S'),
                        'end': d['end'].strftime('%Y-%m-%d %H:%M:%S') if d.get('end') else 'In corso',
                        'duration': d.get('duration'),
                        'duration_formatted': f"{int(d['duration'] // 60)}m {int(d['duration'] % 60)}s" if d.get('duration') else 'In corso',
                        'count': d['count'],
                        'status': d.get('status', 'resolved')
                    }
                    for d in self.disconnections
                ]
            },
            'events': dict(self.stats),
            'transmissions': self.transmissions[:50]  # Mostra solo le prime 50 per performance
        }
    
    def analyze_log(self, content):
        """Analizza il contenuto del log (compatibilità con log_processor.py)"""
        # Reset delle statistiche
        self.transmissions = []
        self.carriers_opened = 0
        self.total_transmission_time = timedelta()
        self.stats = defaultdict(int)
        self.ctcss_tones = defaultdict(int)
        self.talk_groups = defaultdict(int)
        self.qso_sessions = []
        self.active_tg = None
        self.qso_start = None
        # Reset disconnessioni
        self.disconnections = []
        self.current_disconnection = None
        
        tx_sessions = []  # Per tracciare le sessioni ON/OFF
        
        try:
            lines = content.strip().split('\n')
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse del timestamp e del messaggio
                # Supporta sia "Oct 21" che "Nov  1" (con spazio extra per giorni a cifra singola)
                match = re.match(r'^(\w{3} \w{3} \s*\d{1,2} \d{2}:\d{2}:\d{2} \d{4}): (.+)$', line)
                if not match:
                    continue
                    
                timestamp_str, message = match.groups()
                # Normalizza gli spazi extra nel timestamp prima del parsing
                timestamp_str = re.sub(r'\s+', ' ', timestamp_str.strip())
                timestamp = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Y')
                
                # === ANALISI SUBTONI CTCSS ===
                ctcss_match = re.search(r'(\d+\.?\d*) Hz CTCSS tone detected', message)
                if ctcss_match:
                    tone_freq = float(ctcss_match.group(1))
                    self.ctcss_tones[tone_freq] += 1
                    self.stats['ctcss_detections'] += 1
                
                # === ANALISI TALK GROUPS ===
                tg_match = re.search(r'Selecting TG #(\d+)', message)
                if tg_match:
                    tg_id = int(tg_match.group(1))
                    if tg_id != 0:  # Solo per TG diversi da 0
                        self.talk_groups[tg_id] += 1
                        self.stats['tg_selections'] += 1
                
                # === IDENTIFICAZIONE QSO ===
                # QSO più restrittivo: solo con sequenza CTCSS -> TG selection -> TG #0
                
                # Gestione Talk Groups per QSO
                if tg_match:
                    tg_id = int(tg_match.group(1))
                    
                    if tg_id == 0:
                        # TG #0 = fine QSO (solo se abbiamo un TG attivo)
                        if self.active_tg is not None and self.qso_start is not None:
                            duration = (timestamp - self.qso_start).total_seconds()
                            
                            if duration >= 3:  # QSO valido solo se >= 3 secondi (più restrittivo)
                                self.qso_sessions.append({
                                    'tg': self.active_tg,
                                    'start_time': self.qso_start,
                                    'end_time': timestamp,
                                    'duration_seconds': duration
                                })
                                self.stats['valid_qso'] += 1
                        
                        self.qso_start = None
                        self.active_tg = None
                    else:
                        # TG diverso da 0 = possibile inizio QSO
                        # Ma inizia QSO solo se c'è stato un CTCSS prima
                        if self.qso_start is None:
                            # Cerca CTCSS recente (negli ultimi 5 secondi)
                            # Per ora impostiamo start al momento del TG selection
                            self.qso_start = timestamp
                        
                        self.active_tg = tg_id
                
                # CTCSS non inizia più automaticamente i QSO
                # Serve solo come prerequisito per i TG
                
                # === ANALISI TRASMISSIONE ===
                if 'Turning the transmitter ON' in message:
                    tx_sessions.append({
                        'start_time': timestamp,
                        'start_line': line
                    })
                    self.stats['tx_on'] += 1
                
                elif 'Turning the transmitter OFF' in message and tx_sessions:
                    last_session = tx_sessions[-1]
                    if 'end_time' not in last_session:
                        duration = timestamp - last_session['start_time']
                        duration_seconds = duration.total_seconds()
                        
                        if duration_seconds >= 0.1:  # Filtro rumore
                            self.transmissions.append({
                                'start_time': last_session['start_time'],
                                'end_time': timestamp,
                                'duration': duration,
                                'duration_seconds': duration_seconds,
                                'start_line': last_session['start_line'],
                                'end_line': line
                            })
                            self.total_transmission_time += duration
                        
                        last_session['end_time'] = timestamp
                        self.stats['tx_off'] += 1
                
                # === CONTEGGIO PORTANTI ===
                if 'The squelch is OPEN' in message:
                    self.carriers_opened += 1
                    self.stats['squelch_open'] += 1
                elif 'The squelch is CLOSED' in message:
                    self.stats['squelch_closed'] += 1
                
                # === TRACCIAMENTO EVENTI NODI E DISCONNESSIONI ===
                if "Node joined" in message or "Node left" in message:
                    # Eventi di nodi - chiudono eventuali disconnessioni in corso
                    if self.current_disconnection:
                        self.current_disconnection['end'] = timestamp
                        self.current_disconnection['duration'] = (timestamp - self.current_disconnection['start']).total_seconds()
                        self.disconnections.append(self.current_disconnection)
                        self.current_disconnection = None
                    
                    if "Node joined" in message:
                        self.stats['nodes_joined'] += 1
                    else:
                        self.stats['nodes_left'] += 1
                
                # === TRACCIAMENTO DISCONNESSIONI ===
                if "ReflectorLogic: Disconnected from" in message and "Connection timed out" in message:
                    if self.current_disconnection is None:
                        # Inizio nuovo periodo di disconnessione
                        self.current_disconnection = {
                            'start': timestamp,
                            'end': None,
                            'count': 1,
                            'last_disconnection': timestamp
                        }
                    else:
                        # Incrementa il contatore di disconnessioni dello stesso periodo
                        self.current_disconnection['count'] += 1
                        self.current_disconnection['last_disconnection'] = timestamp
                    self.stats['disconnections'] += 1
            
            # Gestione disconnessioni ancora in corso alla fine del log
            if self.current_disconnection:
                # Chiudi il periodo con l'ultima disconnessione rilevata
                self.current_disconnection['end'] = self.current_disconnection['last_disconnection']
                self.current_disconnection['duration'] = (
                    self.current_disconnection['last_disconnection'] - 
                    self.current_disconnection['start']
                ).total_seconds()
                self.current_disconnection['status'] = 'resolved'
                self.disconnections.append(self.current_disconnection)
                self.current_disconnection = None
                
        except Exception as e:
            print(f"Errore durante l'analisi: {e}")
            
        # Statistiche finali - converti timedelta in secondi
        total_seconds = self.total_transmission_time.total_seconds()
        
        # Calcola statistiche durata trasmissioni
        durations = [t['duration_seconds'] for t in self.transmissions]
        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        
        # Calcola statistiche QSO
        qso_durations = [q['duration_seconds'] for q in self.qso_sessions]
        qso_total_time = sum(qso_durations)
        
        # Prepara i subtoni per il display con formato compatibile (ordinati per frequenza)
        total_ctcss_detections = sum(self.ctcss_tones.values())
        sorted_ctcss = []
        for freq, count in sorted(self.ctcss_tones.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_ctcss_detections * 100) if total_ctcss_detections > 0 else 0
            sorted_ctcss.append((freq, {'count': count, 'percentage': round(percentage, 2)}))
        
        # Prepara i TG per il display con formato compatibile (ordinati per frequenza)
        total_tg_selections = sum(self.talk_groups.values())
        sorted_tg = []
        for tg_id, count in sorted(self.talk_groups.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_tg_selections * 100) if total_tg_selections > 0 else 0
            sorted_tg.append((tg_id, {'count': count, 'percentage': round(percentage, 2)}))
        
        # Calcola durate per TG basandosi sui QSO
        tg_durations = {}
        for qso in self.qso_sessions:
            tg = qso.get('tg', 0)
            if tg not in tg_durations:
                tg_durations[tg] = {
                    'total_seconds': 0,
                    'qso_count': 0,
                    'avg_duration': 0
                }
            tg_durations[tg]['total_seconds'] += qso['duration_seconds']
            tg_durations[tg]['qso_count'] += 1
        
        # Calcola durate medie per TG
        for tg in tg_durations:
            avg_seconds = tg_durations[tg]['total_seconds'] / tg_durations[tg]['qso_count']
            tg_durations[tg]['avg_duration'] = avg_seconds
        
        # Ordina TG per durata totale (decrescente)
        sorted_tg_by_duration = sorted(tg_durations.items(), key=lambda x: x[1]['total_seconds'], reverse=True)
        
        # Formato compatibile con log_processor.py
        return {
            'basic': {
                'total_transmissions': len(self.transmissions),
                'total_transmission_time': total_seconds,
                'avg_transmission_time': avg_duration,
                'max_transmission_time': max_duration,
                'min_transmission_time': min_duration,
                'carriers_opened': self.carriers_opened
            },
            'ctcss': {
                'total_detections': sum(self.ctcss_tones.values()),
                'unique_tones': len(self.ctcss_tones),
                'ctcss_list': sorted_ctcss
            },
            'talk_groups': {
                'total_selections': sum(self.talk_groups.values()),
                'unique_tgs': len(self.talk_groups),
                'tg_list': sorted_tg,
                'tg_durations': sorted_tg_by_duration
            },
            'qso': {
                'total_qso': len(self.qso_sessions),
                'total_qso_time': qso_total_time,
                'qso_sessions': self.qso_sessions
            },
            'disconnections': {
                'total_periods': len(self.disconnections),
                'total_disconnections': sum(d['count'] for d in self.disconnections),
                'periods': [
                    {
                        'start': d['start'],
                        'end': d.get('end'),
                        'duration': d.get('duration'),
                        'duration_formatted': f"{int(d['duration'] // 60)}m {int(d['duration'] % 60)}s" if d.get('duration') else 'In corso',
                        'count': d['count'],
                        'status': d.get('status', 'resolved')
                    }
                    for d in self.disconnections
                ]
            },
            'events': dict(self.stats)
        }

# =============================================================================
# FUNZIONI HELPER PER ANALISI LOG
# =============================================================================

def analyze_log_content(content):
    """Funzione helper per analizzare il contenuto di un log"""
    analyzer = SVXLinkLogAnalyzer()
    return analyzer.analyze_log(content)

# =============================================================================
# INIZIALIZZAZIONE MODULI DOPO LA DEFINIZIONE DELLA CLASSE
# =============================================================================

# Ora possiamo importare e inizializzare i moduli che dipendono da SVXLinkLogAnalyzer
if DB_AVAILABLE:
    try:
        # Prova ad inizializzare il DatabaseManager
        db_manager = DatabaseManager()
        print("✅ Database Manager inizializzato")
        
        # Prova ad importare e inizializzare log processor (opzionale per statistiche automatiche)
        try:
            from log_processor import LogProcessor
            log_processor = LogProcessor()
            print("✅ Log Processor inizializzato")
        except Exception as lp_error:
            print(f"⚠️ Log Processor non disponibile: {lp_error}")
            log_processor = None
        
        # Prova ad importare scheduler (opzionale per processamento automatico)
        try:
            from scheduler import init_scheduler, get_scheduler
            scheduler = init_scheduler()
            print("✅ Scheduler inizializzato")
        except Exception as scheduler_error:
            print(f"⚠️ Scheduler non disponibile: {scheduler_error}")
            scheduler = None
        
        print("✅ Database inizializzato - funzionalità base disponibili")
        
    except Exception as e:
        print(f"⚠️ Errore inizializzazione database: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        DB_AVAILABLE = False
        db_manager = None
        log_processor = None
        scheduler = None

# Imposta funzioni per verificare la disponibilità dei moduli
def is_database_available():
    """Verifica se il database è disponibile e funzionante"""
    global db_manager, DB_AVAILABLE
    if not DB_AVAILABLE or db_manager is None:
        return False
    try:
        # Test semplice per verificare che il database funzioni
        db_manager.get_date_range_stats()
        return True
    except Exception as e:
        print(f"⚠️ Database non funzionante: {e}")
        return False

def is_log_processor_available():
    """Verifica se il log processor è disponibile"""
    global log_processor
    return log_processor is not None

def is_scheduler_available():
    """Verifica se lo scheduler è disponibile"""
    global scheduler  
    return scheduler is not None

@app.route('/')
def index():
    """Pagina principale con form di upload"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint per monitoring"""
    from datetime import datetime
    return {
        'status': 'healthy',
        'service': 'SVXLink Log Analyzer',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'reverse_proxy': {
            'application_root': app.config.get('APPLICATION_ROOT'),
            'url_scheme': request.scheme,
            'host': request.host,
            'path': request.path,
            'base_url': request.base_url,
            'url_root': request.url_root
        }
    }

@app.route('/upload', methods=['POST'])
def upload_file():
    """Gestisce l'upload e l'analisi del file"""
    if 'file' not in request.files:
        flash('Nessun file selezionato')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Nessun file selezionato')
        return redirect(request.url)
    
    if file:
        # Salva il file temporaneamente
        filename = f"svxlink_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Analizza il file
            analyzer = SVXLinkLogAnalyzer()
            analyzer.parse_log_file(filepath)
            stats = analyzer.get_statistics()
            
            # Rimuovi il file temporaneo
            os.remove(filepath)
            
            return render_template('results.html', stats=stats, filename=file.filename)
            
        except Exception as e:
            # Rimuovi il file temporaneo in caso di errore
            if os.path.exists(filepath):
                os.remove(filepath)
            flash(f'Errore durante l\'analisi del file: {str(e)}')
            return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint per analisi programmatica"""
    if 'file' not in request.files:
        return {'error': 'Nessun file fornito'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Nessun file selezionato'}, 400
    
    # Salva il file temporaneamente
    filename = f"svxlink_log_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Analizza il file
        analyzer = SVXLinkLogAnalyzer()
        analyzer.parse_log_file(filepath)
        stats = analyzer.get_statistics()
        
        # Rimuovi il file temporaneo
        os.remove(filepath)
        
        return {
            'success': True,
            'filename': file.filename,
            'analysis': stats
        }
        
    except Exception as e:
        # Rimuovi il file temporaneo in caso di errore
        if os.path.exists(filepath):
            os.remove(filepath)
        return {'error': f'Errore durante l\'analisi: {str(e)}'}, 500

# =============================================================================
# ROUTE PER STATISTICHE STORICHE
# =============================================================================

@app.route('/statistics')
def statistics():
    """Pagina principale delle statistiche storiche"""
    if not is_database_available():
        flash('Database non disponibile. Funzionalità statistiche non attive.', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Ottieni range di date disponibili
        date_range = db_manager.get_date_range_stats()
        
        # Ottieni riepilogo processamento
        processing_summary = log_processor.get_processing_summary()
        
        return render_template('statistics.html', 
                             date_range=date_range,
                             processing_summary=processing_summary)
    except Exception as e:
        flash(f'Errore caricamento statistiche: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/statistics/daily')
def api_daily_statistics():
    """API per statistiche giornaliere"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default: ultimi 30 giorni
        if not start_date or not end_date:
            end_date = date.today().isoformat()
            start_date = (date.today() - timedelta(days=30)).isoformat()
        
        # Valida date
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato data non valido. Usa YYYY-MM-DD'}), 400
        
        # Recupera statistiche
        daily_stats = db_manager.get_daily_stats(start_date, end_date)
        
        return jsonify({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'total_days': len(daily_stats),
            'data': daily_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/monthly')
def api_monthly_statistics():
    """API per statistiche mensili"""
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))
        
        # Valida parametri
        if not (1 <= month <= 12):
            return jsonify({'error': 'Mese non valido (1-12)'}), 400
        
        if not (2020 <= year <= 2030):
            return jsonify({'error': 'Anno non valido'}), 400
        
        # Recupera statistiche aggregate mensili
        monthly_stats = db_manager.get_monthly_aggregated_stats(year, month)
        
        return jsonify({
            'success': True,
            'period': {'year': year, 'month': month},
            'data': monthly_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/yearly')
def api_yearly_statistics():
    """API per statistiche annuali"""
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        year = int(request.args.get('year', date.today().year))
        
        # Valida anno
        if not (2020 <= year <= 2030):
            return jsonify({'error': 'Anno non valido'}), 400
        
        # Recupera statistiche aggregate annuali
        yearly_stats = db_manager.get_yearly_aggregated_stats(year)
        
        return jsonify({
            'success': True,
            'period': {'year': year},
            'data': yearly_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/ctcss')
def api_ctcss_statistics():
    """API per statistiche CTCSS"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default: ultimi 30 giorni
        if not start_date or not end_date:
            end_date = date.today().isoformat()
            start_date = (date.today() - timedelta(days=30)).isoformat()
        
        # Recupera statistiche CTCSS
        ctcss_stats = db_manager.get_ctcss_stats(start_date, end_date)
        
        return jsonify({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'total_tones': len(ctcss_stats),
            'data': ctcss_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/talkgroups')
def api_talkgroups_statistics():
    """API per statistiche Talk Groups"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default: ultimi 30 giorni
        if not start_date or not end_date:
            end_date = date.today().isoformat()
            start_date = (date.today() - timedelta(days=30)).isoformat()
        
        # Recupera statistiche TG
        tg_stats = db_manager.get_tg_stats(start_date, end_date)
        
        return jsonify({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'total_tgs': len(tg_stats),
            'data': tg_stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/disconnections')
def api_disconnections_statistics():
    """API per statistiche disconnessioni ReflectorLogic"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default: ultimi 30 giorni
        if not start_date or not end_date:
            end_date = date.today().isoformat()
            start_date = (date.today() - timedelta(days=30)).isoformat()
        
        # Valida date
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato data non valido. Usa YYYY-MM-DD'}), 400
        
        # Recupera statistiche disconnessioni
        disconnections = db_manager.get_disconnections(start_date, end_date)
        
        # Calcola statistiche aggregate
        total_periods = len(disconnections)
        total_disconnections = sum(d.get('disconnection_count', 0) for d in disconnections)
        
        # Calcola durata totale (le durate sono già formattate come stringa nel DB)
        total_duration_formatted = "In corso"
        if disconnections:
            # Se ci sono solo periodi ongoing, mostra "In corso"
            has_resolved = any(d.get('status') == 'resolved' and d.get('duration') for d in disconnections)
            if has_resolved:
                total_duration_formatted = "Vedi dettagli"
            elif all(d.get('status') == 'ongoing' for d in disconnections):
                total_duration_formatted = "In corso"
        
        return jsonify({
            'success': True,
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_periods': total_periods,
                'total_disconnections': total_disconnections,
                'total_duration_formatted': total_duration_formatted
            },
            'data': disconnections
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/process')
def api_process_logs():
    """API per processare nuovi file log"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    if not is_log_processor_available():
        return jsonify({'error': 'Log processor non disponibile - funzionalità automatiche disabilitate'}), 503
    
    try:
        # Processa file non elaborati
        result = log_processor.process_all_files()
        
        return jsonify({
            'success': True,
            'processed': result['processed'],
            'errors': result['errors'],
            'message': f"Processati {result['processed']} file, {result['errors']} errori"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/dates')
def api_available_dates():
    """API per ottenere date disponibili"""
    if not DB_AVAILABLE:
        return jsonify({'error': 'Database non disponibile'}), 503
    
    try:
        dates = db_manager.get_available_dates()
        date_range = db_manager.get_date_range_stats()
        
        return jsonify({
            'success': True,
            'available_dates': dates,
            'date_range': date_range,
            'total_days': len(dates)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/scheduler')
def api_scheduler_status():
    """API per stato dello scheduler"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    if not is_scheduler_available():
        return jsonify({
            'success': True,
            'running': False,
            'scheduler_available': False,
            'message': 'Scheduler non disponibile - funzionalità automatiche disabilitate'
        })
    
    try:
        scheduler_obj = get_scheduler()
        processor_summary = {}
        
        if is_log_processor_available():
            processor_summary = log_processor.get_processing_summary()
        
        return jsonify({
            'success': True,
            'running': scheduler_obj.running if scheduler_obj else False,
            'scheduler_available': True,
            'next_jobs': scheduler_obj.get_next_runs() if scheduler_obj else [],
            'processor_summary': processor_summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics/force-process', methods=['POST'])
def api_force_process():
    """API per forzare processamento immediato"""
    if not is_database_available():
        return jsonify({'error': 'Database non disponibile'}), 503
    
    if not is_scheduler_available():
        return jsonify({'error': 'Scheduler non disponibile - funzionalità automatiche disabilitate'}), 503
    
    try:
        scheduler_obj = get_scheduler()
        result = scheduler_obj.force_process()
        
        return jsonify({
            'success': True,
            'processed': result['processed'],
            'errors': result['errors'],
            'message': f"Processamento forzato: {result['processed']} file elaborati"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reload-db', methods=['POST'])
def reload_database():
    """Ricarica il database manager per sincronizzare con i dati aggiornati"""
    global db_manager, DB_AVAILABLE
    
    try:
        # Crea nuova istanza del database manager
        new_db_manager = DatabaseManager()
        dates = new_db_manager.get_available_dates()
        
        # Aggiorna le variabili globali
        db_manager = new_db_manager
        DB_AVAILABLE = len(dates) > 0
        
        return jsonify({
            'success': True,
            'message': f'Database ricaricato: {len(dates)} date disponibili',
            'dates_count': len(dates),
            'db_available': DB_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/reset-db', methods=['POST'])
def reset_database():
    """Resetta completamente il database eliminando tutti i dati"""
    global db_manager, DB_AVAILABLE
    
    try:
        if not is_database_available():
            return jsonify({'error': 'Database non disponibile'}), 503
            
        # Conta i record prima del reset
        dates_before = db_manager.get_available_dates()
        records_count = len(db_manager.get_all_daily_stats()) if hasattr(db_manager, 'get_all_daily_stats') else 0
        
        # Esegui il reset del database
        db_manager.reset_database()
        
        # Aggiorna le variabili globali
        DB_AVAILABLE = False
        
        return jsonify({
            'success': True,
            'message': f'Database resettato: eliminati {len(dates_before)} giorni di dati',
            'deleted_dates': len(dates_before),
            'deleted_records': records_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status')
def status():
    """Mostra lo stato dell'applicazione"""
    return {
        'database': "✅ Disponibile" if is_database_available() else "❌ Non disponibile",
        'log_processor': "✅ Disponibile" if is_log_processor_available() else "❌ Non disponibile", 
        'scheduler': "✅ Disponibile" if is_scheduler_available() else "❌ Non disponibile",
        'db_available': is_database_available()
    }

if __name__ == '__main__':
    import os
    
    # Configurazione per environment
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    print(f"🚀 Starting SVXLink Log Analyzer...")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🛠️ Debug: {debug_mode}")
    print(f"🌐 URL: http://{host}:{port}")
    
    app.run(debug=debug_mode, host=host, port=port)