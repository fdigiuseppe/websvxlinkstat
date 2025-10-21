# Changelog

Tutte le modifiche importanti a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-21

### 🎉 Nuove Funzionalità Principali

#### 📊 Sistema Statistiche Storiche Complete
- **Dashboard interattiva** con visualizzazioni giornaliere, mensili e annuali
- **Database SQLite persistente** con schema completo per archiviazione dati
- **API REST complete** per statistiche storiche (`/api/statistics/*`)
- **Grafici Chart.js** per trend trasmissioni e distribuzione QSO
- **Tabelle dettagliate** con dati ordinabili e filtrabili
- **Range date personalizzabile** per analisi periodo specifico

#### 🔧 Gestione Database e Manutenzione
- **Reset database completo** con conferma multipla (Web UI, API, Script)
- **Processamento automatico** file nella directory `data/`
- **Force import** per re-elaborazione file esistenti
- **API reload-db** per sincronizzazione stato database
- **Health monitoring** con endpoint `/status` e `/health`

#### 🎨 Interfaccia Utente Migliorata  
- **Pagina statistics** (`/statistics`) con dashboard completa
- **Loading indicators** per feedback visivo operazioni asincrone
- **Error handling migliorato** con messaggi dettagliati
- **Design responsive** ottimizzato per tutti i dispositivi
- **Pulsanti azione** per processamento e reset direttamente dall'UI

### 🔧 Miglioramenti Tecnici

#### 🗄️ Architettura Database
- **Schema strutturato** con tabelle `daily_logs`, `ctcss_stats`, `tg_stats`, `qso_events`
- **Indici ottimizzati** per performance query su date e statistiche
- **Transazioni atomiche** per consistenza dati
- **Gestione errori robusta** con rollback automatico

#### 🐳 Docker e Deployment
- **Persistenza volume** per database tra restart container
- **Configurazione environment** con variabile `DATABASE_PATH`
- **Health checks** automatici per monitoraggio container
- **Multi-stage build** ottimizzato per produzione

#### 🔌 API REST Estese
- `GET /api/statistics/daily` - Statistiche giornaliere con filtri data
- `GET /api/statistics/monthly` - Aggregazioni mensili  
- `GET /api/statistics/yearly` - Dati annuali
- `POST /api/reset-db` - Reset completo database con sicurezza
- `POST /api/reload-db` - Ricarica stato database
- `POST /api/statistics/process` - Processamento forzato nuovi file

### 🛠️ Strumenti di Amministrazione
- **Script `reset_database.py`** - Reset standalone con conferma
- **Script `force_import.py`** - Import forzato con override
- **Logging migliorato** con timestamp e livelli dettaglio
- **Validazione dati** per prevenire corruzione database

### 🔒 Sicurezza e Affidabilità
- **Conferme multiple** per operazioni distruttive (reset DB)
- **Validazione input** per parametri API e form
- **Graceful degradation** quando componenti non disponibili  
- **Error boundaries** per prevenire crash applicazione
- **Backup automatico** dati durante operazioni critiche

## [1.0.0] - 2025-10-19

### ✨ Release Iniziale

#### 🎯 Funzionalità Core
- **Analisi file log SVXLink** con parsing completo eventi
- **Calcolo statistiche** tempo trasmissione, portanti, QSO
- **Rilevamento CTCSS** e Talk Groups con conteggi
- **Interfaccia web** moderna con upload drag & drop
- **Grafici interattivi** per visualizzazione dati
- **API REST** per integrazione programmatica

#### 🏗️ Architettura Base
- **Flask application** con template engine Jinja2
- **Bootstrap UI** responsive e moderna
- **Chart.js integration** per grafici dinamici  
- **Docker containerization** con Compose
- **File processing** in memoria per analisi rapide

#### 📋 Analisi Supportate
- Tempo totale trasmissioni con calcoli precisi
- Conteggio portanti aperte e statistiche durata
- Rilevamento automatico subtoni CTCSS
- Tracking Talk Groups con durate e statistiche
- Identificazione QSO completi con pattern recognition
- Eventi log completi (TX on/off, squelch, connections)

---

## 🔗 Link Utili

- **Repository**: https://github.com/fdigiuseppe/websvxlinkstat
- **Issues**: https://github.com/fdigiuseppe/websvxlinkstat/issues
- **Docker Hub**: (se pubblicato)
- **Documentation**: README.md e DOCKER-README.md

## 📝 Note di Versioning

- **Major version** (x.0.0): Cambio architettura o breaking changes
- **Minor version** (0.x.0): Nuove funzionalità backward-compatible  
- **Patch version** (0.0.x): Bug fix e miglioramenti minori