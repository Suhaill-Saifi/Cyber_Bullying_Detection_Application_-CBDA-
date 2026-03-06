.PHONY: help build up down client logs clean rebuild

CYAN  = \033[0;36m
RESET = \033[0m

help:
	@printf "\n  $(CYAN)SafeChat — Make Commands$(RESET)\n\n"
	@printf "  $(CYAN)make build$(RESET)    Build Docker images\n"
	@printf "  $(CYAN)make up$(RESET)       Start server (detached)\n"
	@printf "  $(CYAN)make client$(RESET)   Connect a new CLI client session\n"
	@printf "  $(CYAN)make logs$(RESET)     Follow server logs\n"
	@printf "  $(CYAN)make down$(RESET)     Stop all containers\n"
	@printf "  $(CYAN)make rebuild$(RESET)  Full clean rebuild (no cache)\n"
	@printf "  $(CYAN)make clean$(RESET)    Remove images and volumes\n\n"

build:
	docker compose build

up:
	docker compose up -d server

client:
	docker compose run --rm client

logs:
	docker compose logs -f server

down:
	docker compose down

rebuild:
	docker compose down --volumes --remove-orphans
	docker compose build --no-cache
	docker compose up -d server

clean:
	docker compose down --volumes --remove-orphans
	docker rmi -f safechat-server:latest safechat-client:latest 2>/dev/null || true
