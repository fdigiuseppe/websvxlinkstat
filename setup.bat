@echo off
REM Setup script per SVXLink Log Analyzer (Windows)

echo 🚀 SVXLink Log Analyzer - Setup
echo =================================

REM Controllo prerequisiti
echo 📋 Controllo prerequisiti...

REM Verifica Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker non trovato. Installa Docker Desktop:
    echo    https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verifica Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose non trovato.
    pause
    exit /b 1
)

echo ✅ Docker e Docker Compose disponibili

REM Copia configurazione environment
if not exist .env (
    echo 📝 Creazione file .env...
    copy .env.example .env >nul
    echo ✅ File .env creato da .env.example
    echo 💡 Modifica .env per personalizzare la configurazione
)

REM Crea directory per i logs
echo 📁 Creazione directory logs...
if not exist logs mkdir logs
echo ✅ Directory logs creata

REM Build dell'immagine Docker
echo 🔨 Build dell'immagine Docker...
docker build -t svxlink-analyzer .
if %errorlevel% neq 0 (
    echo ❌ Errore nel build dell'immagine
    pause
    exit /b 1
)

echo ✅ Immagine Docker creata con successo

REM Avvio dell'applicazione
echo 🚀 Avvio dell'applicazione...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Errore nell'avvio del container
    pause
    exit /b 1
)

echo.
echo 🎉 Setup completato con successo!
echo.
echo 📱 L'applicazione è disponibile su:
echo    🌐 http://localhost:5000
echo.
echo 📋 Comandi utili:
echo    docker-compose logs -f    # Visualizza logs
echo    docker-compose stop       # Ferma l'applicazione
echo    docker-compose down       # Ferma e rimuove container
echo.
echo 📖 Documentazione completa: README.md e DOCKER-README.md
echo.
pause