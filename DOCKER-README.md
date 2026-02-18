# 🐳 SVXLink Log Analyzer - Docker


Containerizzazione dell'applicazione SVXLink Log Analyzer per deployment semplice, portabile e sicuro.

## 🌐 Supporto HTTPS & Reverse Proxy

L'applicazione può essere servita in HTTPS e sotto un path dedicato (`/websvxlinkstat`) tramite Apache come reverse proxy.
Consulta la guida [docs/reverse-proxy-deployment.md](docs/reverse-proxy-deployment.md) e il file di esempio `config/apache-reverse-proxy.conf` per la configurazione.

## 🚀 Quick Start

### Usando Docker Compose (Raccomandato)

```bash
# Clona il repository
git clone <repository-url>
cd websvxlinkstat

# Avvia con Docker Compose (con build automatica)
docker-compose up -d --build

# Oppure avvio rapido senza rebuild
docker-compose up -d

# Verifica che sia in esecuzione
docker-compose ps

# Visualizza i logs
docker-compose logs -f
```

L'applicazione sarà disponibile su: **http://localhost:5000**

### Usando Docker direttamente

```bash
# Build dell'immagine
docker build -t svxlink-analyzer .

# Esecuzione del container
docker run -d \
  --name svxlink-analyzer \
  -p 5000:5000 \
  svxlink-analyzer

# Verifica status
docker ps
```

## 📁 Struttura Files Docker

```
websvxlinkstat/
├── Dockerfile              # Definizione immagine Docker
├── docker-compose.yml      # Orchestrazione container
├── docker-entrypoint.sh    # Script di avvio
├── .dockerignore           # Files esclusi dal build
└── DOCKER-README.md        # Questa documentazione
```

## ⚙️ Configurazione

### Variabili d'Ambiente

- `FLASK_ENV`: Ambiente Flask (default: `production`)
- `FLASK_HOST`: Host di binding (default: `0.0.0.0`)
- `FLASK_PORT`: Porta di ascolto (default: `5000`)

### Volumi Docker

Il docker-compose include un volume opzionale per i file log:

```yaml
volumes:
  - ./logs:/app/logs:ro  # Mount read-only per log files
```

## 🔧 Comandi Utili

### Gestione Container

```bash
# Avvia con build automatica (raccomandato)
docker-compose up -d --build

# Avvio rapido senza rebuild
docker-compose up -d

# Ferma i containers
docker-compose down

# Riavvia i containers
docker-compose restart

# Aggiorna l'immagine (rebuild completo)
docker-compose build --no-cache
docker-compose up -d

# Accesso shell nel container
docker-compose exec svxlink-analyzer bash

# Visualizza logs in tempo reale
docker-compose logs -f svxlink-analyzer
```

### Aggiornamento Applicazione

Quando aggiorni il codice con nuove funzionalità:

```bash
# 1. Scarica gli aggiornamenti
git fetch && git pull

# 2. Rebuild dell'immagine Docker senza cache
docker-compose build --no-cache

# 3. Riavvia il container
docker-compose up -d

# 4. Verifica che la migrazione sia avvenuta
docker-compose logs svxlink-analyzer | grep "Database pronto"
```

**Nota**: Le migrazioni del database vengono eseguite **automaticamente** all'avvio del container tramite lo script `migrate_database.py`. Non è necessario perdere i dati esistenti.

### Migrazione Database Manuale

Se necessario, puoi eseguire manualmente la migrazione:

```bash
# Esegui migrazione nel container in esecuzione
docker-compose exec svxlink-analyzer python migrate_database.py

# Oppure reset completo del database (ATTENZIONE: cancella tutti i dati!)
docker-compose exec svxlink-analyzer python reset_database.py --force
```

### Debug e Troubleshooting

```bash
# Verifica salute container
docker-compose ps

# Ispeziona configurazione
docker-compose config

# Verifica risorse utilizzate
docker stats svxlink-analyzer

# Cleanup completo
docker-compose down -v
docker system prune -f
```

### Troubleshooting Pannello Disconnessioni

Se dopo un aggiornamento non vedi il **pannello Disconnessioni ReflectorLogic**:

```bash
# 1. Verifica che la tabella esista nel database
docker-compose exec svxlink-analyzer sqlite3 /app/data/db/svxlink_stats.db \
  "SELECT name FROM sqlite_master WHERE type='table' AND name='daily_disconnections';"

# 2. Se la tabella non esiste, esegui manualmente la migrazione
docker-compose exec svxlink-analyzer python migrate_database.py

# 3. Riprocessa i log per popolare i dati
docker-compose exec svxlink-analyzer python force_import.py

# 4. Verifica che ci siano dati
docker-compose exec svxlink-analyzer sqlite3 /app/data/db/svxlink_stats.db \
  "SELECT COUNT(*) FROM daily_disconnections;"
```

## 🌐 Accesso all'Applicazione

Una volta avviato il container:

1. **Web Interface**: http://localhost:5000
2. **API Endpoint**: http://localhost:5000/api/analyze
3. **Health Check**: http://localhost:5000/ (per monitoring)

## 📊 Monitoring

Il container include un health check automatico che verifica:
- Risposta dell'applicazione Flask
- Disponibilità del servizio web
- Controllo ogni 30 secondi

```bash
# Verifica health status
docker inspect --format='{{.State.Health.Status}}' svxlink-analyzer
```

## 🔒 Sicurezza

Il container implementa le best practices di sicurezza:

- ✅ **Utente non-root**: L'app gira come utente `appuser`
- ✅ **Immagine minimal**: Base `python:3.11-slim`
- ✅ **No cache pip**: Riduce dimensione immagine
- ✅ **Dockerfile multistage**: Ottimizzato per produzione

## 🚀 Deployment Produzione

### Con Docker Swarm

```bash
# Deploy stack
docker stack deploy -c docker-compose.yml svxlink

# Verifica servizi
docker service ls
```

### Con Kubernetes

```yaml
# Esempio deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: svxlink-analyzer
spec:
  replicas: 2
  selector:
    matchLabels:
      app: svxlink-analyzer
  template:
    metadata:
      labels:
        app: svxlink-analyzer
    spec:
      containers:
      - name: svxlink-analyzer
        image: svxlink-analyzer:latest
        ports:
        - containerPort: 5000
```

## 🔧 Personalizzazioni

### Modifica Porta

```bash
# Nel docker-compose.yml
ports:
  - "8080:5000"  # Cambia porta esterna a 8080
```

### Aggiunta Volumi Personalizzati

```yaml
volumes:
  - ./custom-logs:/app/custom-logs:ro
  - ./config:/app/config:ro
```

### Network Personalizzata

```yaml
networks:
  custom-network:
    external: true
```

## 📝 Note

- **Dimensione immagine**: ~200MB
- **Memoria richiesta**: ~100MB
- **CPU**: Minimal per operazioni normali
- **Storage**: Effimero, logs non persistenti di default
- **Database persistente**: Il volume `svxlink_db` mantiene i dati tra i riavvii
- **Migrazioni automatiche**: Lo schema del database viene aggiornato automaticamente all'avvio
- **Aggiornamenti**: Esegui `docker-compose build --no-cache && docker-compose up -d` per nuove versioni

## 🆘 Supporto

Per problemi con Docker:

1. Verifica logs: `docker-compose logs`
2. Controlla risorse: `docker stats`
3. Testa connettività: `curl http://localhost:5000`
4. Ricostruisci immagine: `docker-compose build --no-cache`