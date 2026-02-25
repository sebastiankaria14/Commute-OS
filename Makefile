# Makefile for CommuteOS (PowerShell compatible on Windows)
# Usage: make <target>
# Note: On Windows, you can also use manage.bat for easier management

.PHONY: help start stop restart logs status clean build test setup

help:
	@echo "CommuteOS Management Commands"
	@echo "=============================="
	@echo "start      - Start all services"
	@echo "stop       - Stop all services"
	@echo "restart    - Restart all services"
	@echo "logs       - View logs (all services)"
	@echo "status     - Check service status"
	@echo "clean      - Remove all containers and volumes"
	@echo "build      - Build all containers"
	@echo "rebuild    - Clean build (no cache)"
	@echo "test       - Run tests"
	@echo "setup      - Verify installation"

start:
	docker-compose up -d
	@echo "Services started! API available at http://localhost:8000"

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

status:
	docker-compose ps

clean:
	docker-compose down -v
	@echo "All data removed!"

build:
	docker-compose build

rebuild:
	docker-compose build --no-cache
	docker-compose up -d

test:
	pytest commuteos/tests/ -v

setup:
	python setup.py

# Individual service commands
api-logs:
	docker-compose logs -f api

routing-logs:
	docker-compose logs -f routing_service

redis-cli:
	docker exec -it commuteos_redis redis-cli

db-shell:
	docker exec -it commuteos_postgres psql -U postgres -d commuteos
