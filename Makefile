# Makefile per SVXLink Log Analyzer Docker

# Variabili
IMAGE_NAME = svxlink-analyzer
CONTAINER_NAME = svxlink-log-analyzer
PORT = 5000

# Comandi principali
.PHONY: help build run stop clean logs shell

help: ## Mostra questo help
	@echo "🐳 SVXLink Log Analyzer - Docker Commands"
	@echo "==========================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build dell'immagine Docker
	@echo "🔨 Building Docker image..."
	docker build -t $(IMAGE_NAME) .

run: ## Avvia il container con Docker Compose
	@echo "🚀 Starting SVXLink Analyzer..."
	docker-compose up -d --build
	@echo "✅ Container avviato! Accedi a: http://localhost:$(PORT)"

quick-run: ## Avvia senza rebuild (più veloce)
	@echo "⚡ Quick starting SVXLink Analyzer..."
	docker-compose up -d
	@echo "✅ Container avviato! Accedi a: http://localhost:$(PORT)"

stop: ## Ferma il container
	@echo "🛑 Stopping container..."
	docker-compose down

restart: ## Riavvia il container
	@echo "🔄 Restarting container..."
	docker-compose restart

logs: ## Visualizza i logs
	@echo "📋 Container logs:"
	docker-compose logs -f

shell: ## Accesso shell nel container
	@echo "🐚 Accessing container shell..."
	docker-compose exec $(CONTAINER_NAME) bash

status: ## Verifica status container
	@echo "📊 Container status:"
	docker-compose ps

clean: ## Cleanup completo (container + immagini)
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi $(IMAGE_NAME) 2>/dev/null || true
	docker system prune -f

rebuild: clean build run ## Ricostruisce e riavvia tutto

dev: ## Avvia in modalità development
	@echo "🛠️ Starting in development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

test: ## Testa l'applicazione
	@echo "🧪 Testing application..."
	curl -f http://localhost:$(PORT)/ || echo "❌ Application not responding"

health: ## Verifica health del container
	@echo "💚 Health check:"
	docker inspect --format='{{.State.Health.Status}}' $(CONTAINER_NAME) || echo "Container not running"

# Comandi avanzati
push: ## Push immagine a registry
	@echo "📤 Pushing to registry..."
	docker tag $(IMAGE_NAME) registry.example.com/$(IMAGE_NAME):latest
	docker push registry.example.com/$(IMAGE_NAME):latest

backup: ## Backup configurazione
	@echo "💾 Creating backup..."
	tar -czf svxlink-backup-$(shell date +%Y%m%d).tar.gz \
		docker-compose.yml Dockerfile requirements.txt app.py templates/

deploy: ## Deploy in produzione
	@echo "🚀 Deploying to production..."
	docker stack deploy -c docker-compose.yml svxlink-stack