# Deployment con Reverse Proxy Apache

Questa guida spiega come configurare l'applicazione SVXLink Log Analyzer per funzionare dietro un reverse proxy Apache con HTTPS.

## Configurazione URL

- **Locale Docker**: `http://localhost:5000`
- **Pubblico**: `https://krpbhomepu.ddns.net/websvxlinkstat`

## Passi per il deployment

### 1. Configurazione Apache

Aggiungi la seguente configurazione al tuo Virtual Host HTTPS (`/etc/apache2/sites-available/000-default-ssl.conf` o simile):

```apache
# Moduli necessari (verifica che siano abilitati)
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule headers_module modules/mod_headers.so

<VirtualHost *:443>
    # ... altre configurazioni SSL esistenti ...
    
    # Reverse proxy per SVXLink Stats
    ProxyPreserveHost On
    ProxyRequests Off
    
    <Location /websvxlinkstat>
        ProxyPass http://localhost:5000/
        ProxyPassReverse http://localhost:5000/
        
        # Headers per il reverse proxy
        ProxyPassReverse /
        RequestHeader set X-Forwarded-Proto "https"
        RequestHeader set X-Forwarded-For %{REMOTE_ADDR}s
        RequestHeader set X-Forwarded-Host %{HTTP_HOST}s
        RequestHeader set X-Forwarded-Prefix "/websvxlinkstat"
    </Location>
</VirtualHost>
```

### 2. Abilitazione moduli Apache

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod rewrite
sudo systemctl reload apache2
```

### 3. Deploy dell'applicazione

```bash
# Nel server di produzione
cd /path/to/websvxlinkstat

# Pull dell'ultima versione
git pull origin master

# Rebuild e riavvio container
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Verifica che sia funzionante
curl http://localhost:5000/health
```

### 4. Test della configurazione

- **Test locale**: `curl -I http://localhost:5000/`
- **Test reverse proxy**: `curl -I https://krpbhomepu.ddns.net/websvxlinkstat/`

## URLs dell'applicazione

- **Home**: `https://krpbhomepu.ddns.net/websvxlinkstat/`
- **Statistiche**: `https://krpbhomepu.ddns.net/websvxlinkstat/statistics`
- **API**: `https://krpbhomepu.ddns.net/websvxlinkstat/api/*`
- **Health check**: `https://krpbhomepu.ddns.net/websvxlinkstat/health`

## Troubleshooting

### Errori comuni

1. **404 Not Found**: Controlla che il path `/websvxlinkstat` sia configurato correttamente in Apache
2. **Redirect loops**: Verifica che `ProxyPassReverse` sia impostato correttamente
3. **Assets non caricati**: I link CSS/JS sono esterni (CDN), dovrebbero funzionare sempre

### Log utili

```bash
# Log Apache
sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log

# Log applicazione Docker
docker-compose logs -f svxlink-analyzer
```

### Verifica configurazione

```bash
# Test diretto container
docker exec -it svxlink-log-analyzer curl http://localhost:5000/health

# Test attraverso Apache
curl -H "X-Forwarded-Proto: https" -H "X-Forwarded-Prefix: /websvxlinkstat" http://localhost:5000/
```

## Variabili d'ambiente

L'applicazione supporta queste variabili per il reverse proxy:

- `SCRIPT_NAME=/websvxlinkstat`: Path di base dell'applicazione
- `FLASK_ENV=production`: Environment di produzione
- `APPLICATION_ROOT=/websvxlinkstat`: Root path per Flask

## Sicurezza

- L'applicazione è configurata per funzionare solo dietro reverse proxy
- Tutti i link sono generati relativamente usando `url_for()`
- Headers HTTPS sono gestiti automaticamente da ProxyFix