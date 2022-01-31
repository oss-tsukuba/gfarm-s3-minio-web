COMPOSE_PROJECT_NAME = gfarm-s3
SUDO = sudo

SUDO = $(shell docker version > /dev/null 2>&1 || echo sudo)
DOCKER = $(SUDO) docker
COMPOSE_V1 = docker-compose
COMPOSE_V2 = docker compose
COMPOSE_SW = $(shell ${COMPOSE_V2} version > /dev/null 2>&1 && echo ${COMPOSE_V2} || echo ${COMPOSE_V1})
COMPOSE = $(SUDO) COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) $(COMPOSE_SW)

# use selfsigned certificate
SSC_COMPOSE = $(COMPOSE) -f docker-compose.selfsigned.yml

ps:
	$(COMPOSE) ps

config-check:
	$(COMPOSE) config

prune:
	$(DOCKER) system prune -f

selfsigned-cert-generate:
	$(SSC_COMPOSE) up

selfsigned-cert-ps:
	$(SSC_COMPOSE) ps

selfsigned-cert-config:
	$(SSC_COMPOSE) config

down:
	$(COMPOSE) down --remove-orphans
	$(MAKE) prune

down-REMOVE_VOLUMES:
	$(COMPOSE) down --volumes --remove-orphans

reborn update:
	$(COMPOSE) build
	$(MAKE) down
	$(COMPOSE) up -d

reborn-withlog:
	$(MAKE) reborn
	$(COMPOSE) logs --follow

build-nocache:
	$(COMPOSE) build --no-cache

stop:
	$(COMPOSE) stop

restart:
	$(COMPOSE) restart

restart-withlog:
	$(MAKE) restart
	$(COMPOSE) logs --follow

restart-proxy:
	$(COMPOSE) restart revproxy

restart-copy_home:
	$(COMPOSE) restart copy_home

shell:
	$(COMPOSE) exec gfminio bash

shell-copy_home:
	$(COMPOSE) exec copy_home bash

shell-revproxy:
	$(COMPOSE) exec revproxy bash

logs:
	$(COMPOSE) logs

logs-follow:
	$(COMPOSE) logs --follow

logs-less:
	$(COMPOSE) logs | less -R

_COMPOSE:
	@echo $(COMPOSE)
