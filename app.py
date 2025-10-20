#!/usr/bin/env python3
"""
SVXLink Log Analyzer - Web Application

Questa applicazione analizza i file di log SVXLink per determinare:
- Tempo totale di utilizzo del ponte per trasmissione (QSO)
- Numero di portanti aperte
- Statistiche dettagliate delle trasmissioni
"""

from flask import Flask, render_template, request, flash, redirect, url_for
import os
from datetime import datetime, timedelta
import re
from collections import defaultdict
import tempfile

app = Flask(__name__)
app.secret_key = 'svxlink_analyzer_secret_key_2024'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
        
        tx_sessions = []  # Per tracciare le sessioni ON/OFF
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse del timestamp e del messaggio
                match = re.match(r'^(\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}): (.+)$', line)
                if not match:
                    continue
                    
                timestamp_str, message = match.groups()
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
                elif "Node joined" in message:
                    self.stats['nodes_joined'] += 1
                elif "Node left" in message:
                    self.stats['nodes_left'] += 1
                elif "identification" in message.lower():
                    self.stats['identifications'] += 1
                    
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
            'events': dict(self.stats),
            'transmissions': self.transmissions[:50]  # Mostra solo le prime 50 per performance
        }

@app.route('/')
def index():
    """Pagina principale con form di upload"""
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)