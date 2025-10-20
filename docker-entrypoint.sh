#!/bin/bash

# Script di avvio per container Docker
echo "🚀 Avvio SVXLink Log Analyzer..."
echo "=================================="

# Verifica che la porta sia specificata
FLASK_PORT=${FLASK_PORT:-5000}
FLASK_HOST=${FLASK_HOST:-0.0.0.0}
FLASK_ENV=${FLASK_ENV:-production}

echo "📡 Server in ascolto su ${FLASK_HOST}:${FLASK_PORT}"
echo "🛠️ Environment: ${FLASK_ENV}"
echo "🌐 Accessibile da: http://localhost:${FLASK_PORT}"
echo "📊 Pronto per analizzare log SVXLink!"
echo "=================================="

# Verifica connettività
echo "🔍 Testing network connectivity..."
netstat -tlnp | grep :${FLASK_PORT} || echo "⚠️ Porta ${FLASK_PORT} non ancora in ascolto"

# Avvia l'applicazione Flask
echo "🎬 Avviando applicazione Flask..."
exec python app.py