#!/bin/bash

# Script di avvio per container Docker
echo "🚀 Avvio SVXLink Log Analyzer..."

# Verifica che la porta sia specificata
FLASK_PORT=${FLASK_PORT:-5000}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}

echo "📡 Server in ascolto su ${FLASK_HOST}:${FLASK_PORT}"
echo "🌐 Accessibile da: http://localhost:${FLASK_PORT}"
echo "📊 Pronto per analizzare log SVXLink!"

# Avvia l'applicazione Flask
exec python app.py