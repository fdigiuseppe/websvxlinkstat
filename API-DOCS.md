# API Documentation

Documentazione completa delle API REST del SVXLink Log Analyzer.

## 🌐 Base URL

```
http://localhost:5000
```

## 📋 Indice API

- [Analisi File Log](#-analisi-file-log)
- [Statistiche Storiche](#-statistiche-storiche)  
- [Gestione Database](#️-gestione-database)
- [Monitoraggio Sistema](#-monitoraggio-sistema)

---

## 📊 Analisi File Log

### POST /api/analyze

Analizza un singolo file di log SVXLink e restituisce statistiche immediate.

#### Request

```http
POST /api/analyze
Content-Type: multipart/form-data

file: (binary) # File .txt o .log di SVXLink
```

#### Response

```json
{
  "success": true,
  "filename": "svxlink_log_2025-10-21.txt",
  "analysis": {
    "transmissions": {
      "total": 286,
      "total_time": "1h 6m 45s",
      "avg_duration": 14.0,
      "max_duration": 103,
      "min_duration": 5
    },
    "carriers": {
      "total": 325
    },
    "ctcss": {
      "85.4": {"count": 45, "percentage": 53.3},
      "123.0": {"count": 25, "percentage": 29.8}
    },
    "talk_groups": {
      "61100": {"count": 125, "duration": "45m 30s"},
      "83": {"count": 45, "duration": "12m 15s"}
    },
    "qso": {
      "total": 63,
      "total_time": "8m 48s"
    }
  }
}
```

#### Esempi

```bash
# Bash
curl -X POST -F "file=@svxlink_log.txt" http://localhost:5000/api/analyze

# Python
import requests
files = {'file': open('svxlink_log.txt', 'rb')}
response = requests.post('http://localhost:5000/api/analyze', files=files)
```

---

## 📈 Statistiche Storiche

### GET /api/statistics/daily

Recupera statistiche giornaliere per un range di date.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| start_date | string | No | Data inizio (YYYY-MM-DD). Default: 30 giorni fa |
| end_date | string | No | Data fine (YYYY-MM-DD). Default: oggi |

#### Response

```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-21",
      "filename": "svxlink_log_2025-10-21.txt",
      "total_transmissions": 286,
      "total_transmission_time": 4005,
      "avg_transmission_time": 14.0,
      "max_transmission_time": 103,
      "min_transmission_time": 5,
      "total_qso": 63,
      "total_qso_time": 528,
      "file_size": 133566,
      "processed_at": "2025-10-21T18:28:11.554490"
    }
  ],
  "period": {
    "start": "2025-09-21",
    "end": "2025-10-21"
  },
  "total_days": 3
}
```

#### Esempi

```bash
# Ultime 2 settimane  
curl "http://localhost:5000/api/statistics/daily?start_date=2025-10-07&end_date=2025-10-21"

# Giorno specifico
curl "http://localhost:5000/api/statistics/daily?start_date=2025-10-21&end_date=2025-10-21"
```

### GET /api/statistics/monthly

Statistiche aggregate per mese specifico.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year | integer | Yes | Anno (es. 2025) |
| month | integer | Yes | Mese (1-12) |

#### Response

```json
{
  "success": true,
  "data": {
    "year": 2025,
    "month": 10,
    "total_days": 3,
    "total_transmissions": 858,
    "total_time": 12015,
    "total_qso": 189,
    "avg_daily_transmissions": 286.0,
    "peak_transmissions": 286,
    "min_transmissions": 286,
    "top_ctcss": [
      {"ctcss_frequency": 85.4, "total_count": 135},
      {"ctcss_frequency": 123.0, "total_count": 75}
    ]
  }
}
```

#### Esempi

```bash
# Ottobre 2025
curl "http://localhost:5000/api/statistics/monthly?year=2025&month=10"
```

### GET /api/statistics/yearly

Statistiche aggregate annuali.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| year | integer | Yes | Anno (es. 2025) |

#### Response

```json
{
  "success": true,
  "data": {
    "year": 2025,
    "total_days": 365,
    "total_transmissions": 104500,
    "total_time": 450000,
    "total_qso": 23500,
    "avg_daily_transmissions": 286.3,
    "peak_transmissions": 450,
    "min_transmissions": 12
  }
}
```

---

## 🔧 Gestione Database

### POST /api/reload-db

Ricarica lo stato del database per sincronizzare con nuovi dati.

#### Request

```http
POST /api/reload-db
Content-Type: application/json
```

#### Response

```json
{
  "success": true,
  "message": "Database ricaricato: 3 date disponibili",
  "dates_count": 3,
  "db_available": true
}
```

### POST /api/reset-db

⚠️ **ATTENZIONE**: Elimina completamente tutti i dati dal database.

#### Request

```http
POST /api/reset-db
Content-Type: application/json
```

#### Response

```json
{
  "success": true,
  "message": "Database resettato: eliminati 3 giorni di dati",
  "deleted_dates": 3,
  "deleted_records": 15
}
```

### POST /api/statistics/process

Forza il processamento di nuovi file nella directory `data/`.

#### Response

```json
{
  "success": true,
  "processed": 2,
  "errors": 0,
  "message": "Processamento forzato: 2 file elaborati"
}
```

---

## 🔍 Monitoraggio Sistema

### GET /status

Stato generale dell'applicazione.

#### Response

```json
{
  "database": "✅ Disponibile",
  "log_processor": "✅ Disponibile", 
  "scheduler": "✅ Disponibile",
  "db_available": true
}
```

### GET /health

Health check per monitoring automatico.

#### Response

```json
{
  "status": "healthy",
  "service": "SVXLink Log Analyzer",
  "version": "2.0.0",
  "timestamp": "2025-10-21T20:15:30.123456"
}
```

---

## 🔒 Error Responses

Tutte le API utilizzano codici di stato HTTP standard e formato di errore consistente.

### Errori Comuni

#### 400 Bad Request
```json
{
  "success": false,
  "error": "File non fornito o formato non valido"
}
```

#### 503 Service Unavailable  
```json
{
  "success": false,
  "error": "Database non disponibile"
}
```

#### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Errore interno del server: dettagli specifici"
}
```

---

## 🚀 Rate Limiting e Limiti

### File Upload
- **Dimensione massima**: 16MB per file
- **Formati supportati**: `.txt`, `.log`
- **Timeout**: 30 secondi per processamento

### API Calls
- **Rate limiting**: Non implementato (uso interno)
- **Concurrent requests**: Supportate con SQLite WAL mode
- **Timeout**: 30 secondi per query complesse

---

## 📝 Esempi Completi

### Python Client

```python
import requests
import json

class SVXLinkAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def analyze_file(self, filepath):
        """Analizza un file di log"""
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/api/analyze", files=files)
            return response.json()
    
    def get_daily_stats(self, start_date, end_date):
        """Recupera statistiche giornaliere"""
        params = {'start_date': start_date, 'end_date': end_date}
        response = requests.get(f"{self.base_url}/api/statistics/daily", params=params)
        return response.json()
    
    def reset_database(self):
        """Reset completo database"""
        response = requests.post(f"{self.base_url}/api/reset-db")
        return response.json()

# Utilizzo
api = SVXLinkAPI()
result = api.analyze_file("svxlink_log.txt")
stats = api.get_daily_stats("2025-10-19", "2025-10-21")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class SVXLinkAPI {
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
    }
    
    async analyzeFile(filepath) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filepath));
        
        const response = await axios.post(`${this.baseURL}/api/analyze`, form, {
            headers: form.getHeaders()
        });
        return response.data;
    }
    
    async getDailyStats(startDate, endDate) {
        const response = await axios.get(`${this.baseURL}/api/statistics/daily`, {
            params: { start_date: startDate, end_date: endDate }
        });
        return response.data;
    }
}
```

---

## 🔗 Links Correlati

- [README.md](README.md) - Documentazione generale
- [DOCKER-README.md](DOCKER-README.md) - Setup Docker  
- [CHANGELOG.md](CHANGELOG.md) - Cronologia versioni