#!/bin/bash

# Script per diagnosticare problemi di connettività Docker

echo "🔍 SVXLink Log Analyzer - Diagnostica Docker"
echo "=============================================="

# Info container
echo "📦 Container info:"
docker ps --filter name=svxlink-log-analyzer --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🏥 Health check:"
docker inspect svxlink-log-analyzer --format='{{.State.Health.Status}}' 2>/dev/null || echo "Health check non disponibile"

echo ""
echo "📋 Logs recenti:"
docker logs --tail 20 svxlink-log-analyzer

echo ""
echo "🌐 Test connettività interna container:"
docker exec svxlink-log-analyzer curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ 2>/dev/null || echo "Curl non riuscito"

echo ""
echo "🔌 Porte in ascolto nel container:"
docker exec svxlink-log-analyzer netstat -tlnp 2>/dev/null | grep :5000 || echo "Porta 5000 non in ascolto"

echo ""
echo "🖥️ Test dall'host:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/ 2>/dev/null || echo "❌ Connessione fallita dall'host"

echo ""
echo "🔍 Processi Flask nel container:"
docker exec svxlink-log-analyzer ps aux | grep -i python || echo "Nessun processo Python trovato"

echo ""
echo "💾 Uso risorse container:"
docker stats --no-stream svxlink-log-analyzer 2>/dev/null || echo "Stats non disponibili"