#!/bin/bash

# Setup script per SVXLink Log Analyzer

echo "🚀 SVXLink Log Analyzer - Setup"
echo "================================="

# Controllo prerequisiti
echo "📋 Controllo prerequisiti..."

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non trovato. Installa Docker Desktop:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Verifica Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non trovato."
    exit 1
fi

echo "✅ Docker e Docker Compose disponibili"

# Copia configurazione environment
if [ ! -f .env ]; then
    echo "📝 Creazione file .env..."
    cp .env.example .env
    echo "✅ File .env creato da .env.example"
    echo "💡 Modifica .env per personalizzare la configurazione"
fi

# Crea directory per i logs
echo "📁 Creazione directory logs..."
mkdir -p logs
echo "✅ Directory logs creata"

# Build dell'immagine Docker
echo "🔨 Build dell'immagine Docker..."
docker build -t svxlink-analyzer . || {
    echo "❌ Errore nel build dell'immagine"
    exit 1
}

echo "✅ Immagine Docker creata con successo"

# Avvio dell'applicazione
echo "🚀 Avvio dell'applicazione..."
docker-compose up -d || {
    echo "❌ Errore nell'avvio del container"
    exit 1
}

echo ""
echo "🎉 Setup completato con successo!"
echo ""
echo "📱 L'applicazione è disponibile su:"
echo "   🌐 http://localhost:5000"
echo ""
echo "📋 Comandi utili:"
echo "   docker-compose logs -f    # Visualizza logs"
echo "   docker-compose stop       # Ferma l'applicazione"
echo "   docker-compose down       # Ferma e rimuove container"
echo "   make help                 # Mostra tutti i comandi"
echo ""
echo "📖 Documentazione completa: README.md e DOCKER-README.md"