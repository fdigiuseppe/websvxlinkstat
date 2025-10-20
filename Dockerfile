# Utilizza un'immagine base Python ufficiale
FROM python:3.11-slim

# Imposta il maintainer
LABEL maintainer="SVXLink Log Analyzer"
LABEL description="Web application per analisi log SVXLink con statistiche avanzate"

# Installa curl per healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia i file dei requirements per sfruttare la cache Docker
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice dell'applicazione
COPY . .

# Rendi eseguibile lo script di entrypoint
RUN chmod +x docker-entrypoint.sh

# Crea un utente non-root per sicurezza
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Espone la porta 5000
EXPOSE 5000

# Imposta le variabili d'ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# Comando per avviare l'applicazione
CMD ["./docker-entrypoint.sh"]