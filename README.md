# SVXLink Log Analyzer 📊

Una web application completa in Python Flask che analizza i file di log SVXLink per fornire statistiche storiche dettagliate sulle trasmissioni radio con database persistente e dashboard interattiva.

## 🚀 Caratteristiche Principali

### 📈 Sistema Completo di Statistiche Storiche
- **Database SQLite persistente**: Archiviazione permanente di tutte le statistiche
- **Dashboard interattiva**: Visualizzazione completa con grafici e tabelle dinamiche  
- **Analisi multi-periodo**: Statistiche giornaliere, mensili e annuali
- **Range date personalizzabile**: Filtra dati per periodi specifici
- **Processamento automatico**: Import automatico di nuovi file log
- **Sezioni Avanzate Dashboard**:
  - **Subtoni CTCSS Rilevati**: Tabella con frequenze, rilevazioni totali e percentuali medie
  - **Talk Groups Utilizzati**: Visualizzazione TG con trasmissioni, durate totali e QSO
  - **Riepilogo Talk Groups**: Grafici interattivi (barre e torta) per distribuzione trasmissioni e durate per TG

### 🔍 Analisi Avanzate Log SVXLink
- **Analisi del tempo di trasmissione**: Calcola il tempo totale di utilizzo del ponte per le trasmissioni QSO
- **Conteggio portanti**: Determina quante portanti sono state aperte durante la sessione
- **Analisi subtoni CTCSS**: Rilevamento e conteggio dei subtoni utilizzati con frequenze specifiche
- **Analisi Talk Groups**: Tracciamento e statistiche dei TG aperti durante le sessioni
- **Analisi durate TG**: Calcolo delle durate totali e medie per ogni Talk Group
- **Rilevamento QSO avanzato**: Identificazione automatica di QSO completi basata su pattern di subtoni e TG

### 🎨 Interfaccia Moderna e Funzionale
- **Design responsive**: Interfaccia moderna ottimizzata per desktop e mobile
- **Upload drag & drop**: Caricamento file intuitivo con validazione
- **Grafici interattivi**: Chart.js per visualizzazioni dinamiche
- **Tabelle ordinate**: Dati tabulari con ordinamento e filtri
- **Loading indicators**: Feedback visivo per operazioni lunghe

### 🔧 Funzionalità di Amministrazione
- **Reset database**: Cancellazione completa dati con conferma di sicurezza
- **Processamento forzato**: Re-elaborazione file esistenti
- **API REST complete**: Automazione e integrazione programmatica
- **Health monitoring**: Endpoint di stato per monitoraggio sistema

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

3. **Per analisi singola**: Carica file di log dalla pagina principale
4. **Per statistiche storiche**: Vai su `/statistics` per la dashboard completa
5. **Processamento automatico**: I file nella cartella `data/` vengono processati automaticamente

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

### 📞 Talk Groups & Statistiche Storiche
- **TG attivi**: 4 Talk Groups nel database
- **TG più utilizzato**: TG #61100 (59.5% trasmissioni)
- **Durate totali**: 
  - TG #61100: 45m 30s (25 QSO, media 1m 82s)
  - TG #83: 12m 15s (8 QSO, media 1m 32s)
  - Altri TG con statistiche dettagliate

### 📈 Dashboard Esempio (3 giorni di dati)
- **Periodo analizzato**: 19-21 Ottobre 2025  
- **Giorni totali**: 3 giorni con dati
- **Trasmissioni totali**: 858 trasmissioni
- **Tempo totale**: 12h 15m di attività
- **QSO totali**: 189 conversazioni complete
- **Grafici**: Trend giornaliero + distribuzione QSO per data

## Formato File Log

L'applicazione riconosce il formato standard dei log SVXLink:
```
Sun Oct 19 08:02:33 2025: Tx1: Turning the transmitter ON
Sun Oct 19 08:02:43 2025: Tx1: Turning the transmitter OFF
```

## 🔌 API REST Complete

### Analisi Singola
```bash
# Analizza un singolo file
POST /api/analyze
curl -X POST -F "file=@svxlink_log.txt" http://localhost:5000/api/analyze
```

### Statistiche Storiche
```bash
# Statistiche giornaliere
GET /api/statistics/daily?start_date=2025-10-19&end_date=2025-10-21

# Statistiche mensili  
GET /api/statistics/monthly?year=2025&month=10

# Statistiche annuali
GET /api/statistics/yearly?year=2025

# Statistiche CTCSS (Subtoni)
GET /api/statistics/ctcss?start_date=2025-10-19&end_date=2025-10-21

# Statistiche Talk Groups
GET /api/statistics/talkgroups?start_date=2025-10-19&end_date=2025-10-21
```

### Gestione Database
```bash
# Ricarica stato database
POST /api/reload-db

# Reset completo database (⚠️ ATTENZIONE)
POST /api/reset-db

# Processamento forzato nuovi file
POST /api/statistics/process
```

### Monitoraggio Sistema
```bash
# Stato applicazione
GET /status

# Health check
GET /health
```

## Struttura Progetto

```
websvxlinkstat/
├── app.py                    # Applicazione Flask principale
├── database.py               # Gestione database SQLite
├── log_processor.py          # Processore log SVXLink  
├── force_import.py           # Script import forzato file
├── reset_database.py         # Script reset database
├── database_schema.sql       # Schema database
├── templates/
│   ├── index.html           # Pagina upload
│   ├── results.html         # Pagina risultati analisi
│   └── statistics.html      # Dashboard statistiche storiche
├── data/                    # Directory file log e database
│   ├── svxlink_log_*.txt    # File log SVXLink
│   └── db/                  # Database SQLite
├── requirements.txt         # Dipendenze Python
├── README.md               # Documentazione principale
├── DOCKER-README.md        # Documentazione Docker
├── Dockerfile              # Definizione container Docker
├── docker-compose.yml      # Orchestrazione container
├── docker-compose.dev.yml  # Override per development
├── docker-entrypoint.sh    # Script avvio container
├── .dockerignore           # Files esclusi da Docker
├── .env.example            # Template configurazione
├── Makefile               # Automazione comandi
├── setup.sh               # Setup automatico (Linux/Mac)
└── setup.bat              # Setup automatico (Windows)
```

## 💻 Tecnologie e Stack

- **Backend**: Python 3.11+ con Flask 3.0+
- **Database**: SQLite3 con persistenza su volume Docker
- **Frontend**: HTML5, CSS3, JavaScript ES6, Bootstrap 5.3
- **Grafici**: Chart.js per visualizzazioni interattive
- **Icons**: Font Awesome 6.4
- **Containerizzazione**: Docker & Docker Compose
- **Build Tools**: Makefile per automazione
- **Architettura**: Microservice containerizzato con volume persistence

## 🎯 Funzionalità Complete

### 📊 Dashboard Statistiche Storiche
- **Multi-view**: Visualizzazioni giornaliere, mensili e annuali
- **Grafici interattivi**: Trend trasmissioni e distribuzione QSO
- **Tabelle dettagliate**: Dati completi con ordinamento e filtri
- **Range date dinamico**: Selezione periodi personalizzati
- **Statistiche riepilogative**: Card con metriche principali
- **Auto-refresh**: Aggiornamento automatico dati

### 🔧 Gestione Database e Manutenzione  
- **Database persistente**: SQLite con backup automatico su volume
- **Reset database**: Cancellazione completa con conferma multipla
- **Processamento batch**: Import automatico file dalla cartella data
- **Force import**: Re-processamento file esistenti
- **API reload**: Sincronizzazione stato database in tempo reale
- **Health monitoring**: Controllo stato componenti sistema

### 🎨 Interfaccia Utente Avanzata
- **Upload drag & drop**: Caricamento intuitivo file log
- **Validazione client-side**: Controllo formato e dimensioni
- **Design responsive**: Ottimizzato per desktop, tablet e mobile  
- **Loading indicators**: Feedback visivo operazioni asincrone
- **Error handling**: Gestione errori user-friendly
- **Grafici Chart.js**: Visualizzazioni interattive e responsive

### 🐳 Docker Production Ready
- **Containerizzazione completa**: Docker Compose multi-container
- **Persistence volumes**: Database e log persistenti tra restart
- **Health checks**: Monitoraggio automatico stato container
- **Environment configuration**: Configurazione tramite variabili ambiente
- **Security**: Container non-root, immagini minimal Alpine
- **Development mode**: Hot-reload per sviluppo
- **Production optimization**: Multi-stage build ottimizzato

## ⚙️ Configurazione e Setup

### 🔄 Reset Database
```bash
# Via Web UI - Pulsante rosso nella dashboard
# Via Script
docker exec -it websvxlinkstat-app-1 python3 reset_database.py

# Via API  
curl -X POST http://localhost:5000/api/reset-db
```

### 📁 Gestione File Log
```bash
# Posiziona i file nella directory data/
cp svxlink_log_2025-*.txt ./data/

# Processamento automatico al restart container
docker-compose restart

# Processamento manuale forzato  
docker exec -it websvxlinkstat-app-1 python3 force_import.py
```

### 🔍 Monitoraggio e Debug
```bash
# Controllo stato applicazione
curl http://localhost:5000/status

# Logs container
docker-compose logs -f app

# Accesso shell container
docker exec -it websvxlinkstat-app-1 sh
```

## 📋 Limiti e Specifiche

- **File upload**: Dimensione massima 16MB per file singolo
- **Formati supportati**: .txt, .log (formato standard SVXLink)
- **Database**: SQLite (per installazioni più grandi considerare PostgreSQL)
- **Performance**: Ottimizzato per file fino a 100MB, analisi limitata per performance
- **Concurrent users**: Adatto per uso singolo/piccoli gruppi (per high-traffic usare load balancer)

---

## 📚 Documentazione Completa

- **[API Documentation](API-DOCS.md)** - Guida completa alle API REST
- **[Changelog](CHANGELOG.md)** - Cronologia versioni e modifiche
- **[Docker Setup](DOCKER-README.md)** - Guida deployment Docker (se presente)

## 🤝 Contributi

Il progetto è open source e accetta contributi dalla comunità radioamatoriale:

1. **Fork** il repository
2. **Crea** un branch per le modifiche (`git checkout -b feature/nuova-funzionalita`)
3. **Commit** le modifiche (`git commit -am 'Aggiunge nuova funzionalità'`)
4. **Push** al branch (`git push origin feature/nuova-funzionalita`)  
5. **Crea** una Pull Request

### 🐛 Segnalazione Bug

- Usa GitHub Issues per segnalare problemi
- Includi log dettagliati e file di esempio
- Specifica versione Docker/Python utilizzata

### 💡 Richieste Funzionalità

- Proponi nuove funzionalità via GitHub Issues
- Descrivi il caso d'uso specifico
- Condividi mockup o esempi se disponibili

## 📄 Licenza

Progetto open source per la comunità radioamatoriale.

**MIT License** - Vedi [LICENSE](LICENSE) file per dettagli completi.

---

## 🏷️ Versione Corrente: 2.0.0

🎉 **Nuove funzionalità principali della v2.0.0:**
- Dashboard statistiche storiche completa
- Database persistente con API REST estese  
- Reset database e strumenti di manutenzione
- Grafici interattivi e tabelle dinamiche
- Container Docker production-ready con volumi

📋 **Prossimi sviluppi pianificati:**
- Export PDF/Excel delle statistiche
- Sistema notifiche per anomalie
- Integrazione Grafana per monitoring
- Supporto database PostgreSQL
- API WebSocket per real-time updates