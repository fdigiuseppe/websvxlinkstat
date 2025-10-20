# SVXLink Log Analyzer

Una web application in Python Flask che analizza i file di log SVXLink per fornire statistiche dettagliate sulle trasmissioni radio.

## Caratteristiche

- **Analisi del tempo di trasmissione**: Calcola il tempo totale di utilizzo del ponte per le trasmissioni QSO
- **Conteggio portanti**: Determina quante portanti sono state aperte durante la sessione
- **Analisi subtoni CTCSS**: Rilevamento e conteggio dei subtoni utilizzati con frequenze specifiche
- **Analisi Talk Groups**: Tracciamento e statistiche dei TG aperti durante le sessioni
- **Analisi durate TG**: Calcolo delle durate totali e medie per ogni Talk Group
- **Rilevamento QSO avanzato**: Identificazione automatica di QSO completi basata su pattern di subtoni e TG
- **Statistiche dettagliate**: Fornisce analisi complete degli eventi del log
- **Interfaccia web moderna**: Design responsive con drag & drop per l'upload dei file
- **Grafici interattivi**: Visualizzazione grafica delle statistiche con grafici a torta per durate TG
- **API REST**: Endpoint per analisi programmatica

## Installazione

### Metodo 1: Installazione Tradizionale

1. Clona o scarica il repository
2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

### Metodo 2: Docker (Raccomandato) 🐳

**Quick Start con Docker Compose:**
```bash
# Clona il repository
git clone <repository-url>
cd websvxlinkstat

# Avvia con Docker
docker-compose up -d

# Accedi all'applicazione
# http://localhost:5000
```

**Oppure con Docker direttamente:**
```bash
# Build dell'immagine
docker build -t svxlink-analyzer .

# Esecuzione
docker run -d -p 5000:5000 svxlink-analyzer
```

📖 **Documentazione Docker completa**: Vedi [DOCKER-README.md](DOCKER-README.md)

## Utilizzo

1. Avvia l'applicazione:
```bash
python app.py
```

2. Apri il browser all'indirizzo: http://localhost:5000

3. Carica il tuo file di log SVXLink (formato .txt o .log)

4. Visualizza i risultati dell'analisi

## Analisi Supportate

### Metriche Principali
- **Tempo totale di trasmissione**: Somma di tutti i periodi in cui il trasmettitore è stato attivo
- **Portanti aperte**: Numero totale di volte che il trasmettitore è stato acceso
- **Durata media/min/max**: Statistiche sulla durata delle trasmissioni

### Analisi Avanzate CTCSS e TG
- **Subtoni CTCSS**: Rilevamento automatico di tutti i subtoni utilizzati (es. 85.4 Hz, 123.0 Hz)
  - Conteggio per frequenza specifica
  - Percentuali di utilizzo
  - Identificazione del subtono dominante
- **Talk Groups**: Tracciamento delle selezioni TG (es. TG #61100, TG #32)
  - Conteggio aperture per ogni TG
  - Statistiche di utilizzo
  - TG più attivi
  - **Durate TG**: Calcolo durata totale e media per ogni Talk Group
  - **Grafici durate**: Visualizzazione grafica delle durate con grafici a torta
  - **Tabelle riassuntive**: Tabelle dettagliate con durate, numero QSO e medie per TG

### QSO Detection Intelligente
- **Pattern Recognition**: Identificazione automatica di QSO completi basata su:
  - Rilevamento subtono CTCSS (es. `85.4 Hz CTCSS tone detected`)
  - Apertura Talk Group specifico (es. `Selecting TG #61100`)
  - Chiusura con ritorno a TG #0 (es. `Selecting TG #0`)
- **Metriche QSO**: Durata, TG utilizzato, timestamp inizio/fine
- **Statistiche QSO**: Tempo totale, durata media, QSO più lungo/breve

### Analisi Durate Talk Groups 📊
- **Calcolo automatico durate**: Basato su eventi "Talker start/stop on TG"
- **Metriche per TG**:
  - Durata totale di utilizzo per ogni Talk Group
  - Numero di QSO rilevati per TG
  - Durata media per QSO per ogni TG
- **Visualizzazioni**:
  - **Grafico a ciambella**: Distribuzione durate tra i diversi TG
  - **Tabella riepilogativa**: Dettagli completi con durate formattate (mm:ss)
  - **Percentuali di utilizzo**: Mostra quale TG è più utilizzato
- **Ordinamento intelligente**: TG ordinati per durata totale (dal più utilizzato)

### Eventi Tracciati
- Accensioni e spegnimenti del trasmettitore
- Rilevamenti toni CTCSS con frequenza specifica
- Aperture e chiusure del squelch
- Eventi talker (inizio/fine trasmissione) per calcolo durate TG
- Connessioni/disconnessioni nodi
- Identificazioni automatiche del ripetitore
- Selezioni Talk Group con tracciamento durate

## Esempio Risultati

Con un file di log SVXLink tipico, l'applicazione produce risultati come:

### 📊 Statistiche Generali
- **Tempo totale trasmissione**: 1h 6m 45s (4.64% del giorno)
- **Portanti aperte**: 325 trasmissioni
- **QSO rilevati**: 42 conversazioni complete

### 🎵 Analisi CTCSS
- **Toni rilevati**: 5 frequenze diverse
- **Tono dominante**: 85.4 Hz (53.3% utilizzo)
- **Altri toni**: 123.0 Hz, 91.5 Hz, etc.

### 📞 Talk Groups
- **TG attivi**: 4 Talk Groups
- **TG più utilizzato**: TG #61100 (59.5% trasmissioni)
- **Durate totali**: 
  - TG #61100: 45m 30s (25 QSO, media 1m 82s)
  - TG #83: 12m 15s (8 QSO, media 1m 32s)
  - Altri TG con statistiche dettagliate

## Formato File Log

L'applicazione riconosce il formato standard dei log SVXLink:
```
Sun Oct 19 08:02:33 2025: Tx1: Turning the transmitter ON
Sun Oct 19 08:02:43 2025: Tx1: Turning the transmitter OFF
```

## API REST

### POST /api/analyze
Analizza un file di log tramite API.

**Request**: Multipart form data con campo "file"
**Response**: JSON con risultati dell'analisi

Esempio:
```bash
curl -X POST -F "file=@svxlink_log.txt" http://localhost:5000/api/analyze
```

## Struttura Progetto

```
websvxlinkstat/
├── app.py                 # Applicazione Flask principale
├── templates/
│   ├── index.html        # Pagina di upload
│   └── results.html      # Pagina risultati
├── requirements.txt      # Dipendenze Python
├── README.md            # Documentazione principale
├── DOCKER-README.md     # Documentazione Docker
├── Dockerfile           # Definizione container Docker
├── docker-compose.yml   # Orchestrazione container
├── docker-compose.dev.yml # Override per development
├── docker-entrypoint.sh # Script avvio container
├── .dockerignore        # Files esclusi da Docker
├── .env.example         # Template configurazione
├── Makefile            # Automazione comandi
├── setup.sh            # Setup automatico (Linux/Mac)
├── setup.bat           # Setup automatico (Windows)
└── logs/               # Directory per log files
```

## Tecnologie Utilizzate

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Grafici**: Chart.js
- **Icons**: Font Awesome
- **Containerizzazione**: Docker & Docker Compose
- **Build Tools**: Makefile per automazione

## Funzionalità Avanzate

- Upload via drag & drop
- Validazione file client-side
- Gestione errori completa
- Design responsive per mobile
- Grafici interattivi con Chart.js
  - Timeline eventi significativi
  - Grafici a torta per distribuzione CTCSS
  - **Grafici durate Talk Groups** con visualizzazione a ciambella
- Analisi dettagliata eventi log
- **Tabelle riassuntive TG** con durate totali, numero QSO e durate medie
- Calcolo automatico durate basato su eventi "Talker start/stop"

### 🐳 Docker Features
- **Containerizzazione completa** con Docker e Docker Compose
- **Setup automatico** con script `setup.sh` / `setup.bat`
- **Makefile** per automazione comandi Docker
- **Multi-stage build** ottimizzato per produzione
- **Health checks** automatici per monitoring
- **Configurazione environment** con file `.env`
- **Modalità development** con hot-reload
- **Sicurezza**: Utente non-root, immagine minimal

## Limiti

- Dimensione massima file: 16MB
- Formati supportati: .txt, .log
- Analisi limitata ai primi 50 eventi per performance

## Licenza

Progetto open source per la comunità radioamatoriale.