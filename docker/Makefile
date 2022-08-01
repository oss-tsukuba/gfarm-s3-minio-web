COMPOSE_PROJECT_NAME = gfarm-s3

ENV_FILE = --env-file config.env

SUDO = $(shell docker version > /dev/null 2>&1 || echo sudo)
DOCKER = $(SUDO) docker
COMPOSE_V1 = docker-compose
COMPOSE_V2 = docker compose
COMPOSE_SW = $(shell ${COMPOSE_V2} version > /dev/null 2>&1 && echo ${COMPOSE_V2} || echo ${COMPOSE_V1})
COMPOSE = $(SUDO) COMPOSE_PROJECT_NAME=$(COMPOSE_PROJECT_NAME) $(COMPOSE_SW) $(ENV_FILE)

# use selfsigned certificate
SSC_COMPOSE = $(COMPOSE) -f docker-compose.selfsigned.yml

CONTAINERS = gfminio copy_home revproxy

.PONY =

define gentarget
	$(foreach name,$(CONTAINERS),$(1)@$(name))
endef

TARGET_LOGS = $(call gentarget,logs)
.PONY += $(TARGET_LOGS)

TARGET_LOGS_FOLLOW = $(call gentarget,logs-follow)
.PONY += $(TARGET_LOGS_FOLLOW)

TARGET_LOGS_TIME = $(call gentarget,logs-time)
.PONY += $(TARGET_LOGS_TIME)

ps:
	$(COMPOSE) ps

config-check:
	$(COMPOSE) config

prune:
	$(DOCKER) system prune -f

selfsigned-cert-generate:
	$(SSC_COMPOSE) up
	$(SSC_COMPOSE) down

selfsigned-cert-ps:
	$(SSC_COMPOSE) ps

selfsigned-cert-check-config:
	$(SSC_COMPOSE) config

check-config:
	$(COMPOSE) config

down:
	$(COMPOSE) down --remove-orphans
	$(MAKE) prune

down-REMOVE_VOLUMES:
	$(COMPOSE) down --volumes --remove-orphans

reborn-nowait:
	$(COMPOSE) build
	$(MAKE) down
	$(COMPOSE) up -d

reborn:
	$(MAKE) reborn-nowait
	./wait.sh

reborn-withlog:
	$(MAKE) reborn-nowait
	$(MAKE) logs-follow

build-nocache:
	$(COMPOSE) build --no-cache

stop:
	$(COMPOSE) stop

restart:
	$(COMPOSE) restart

restart-withlog:
	$(MAKE) restart
	$(COMPOSE) logs --follow gfminio

restart@revproxy:
	$(COMPOSE) restart revproxy

restart@copy_home copy-home:
	$(COMPOSE) restart copy_home

reset-brute-force-attack-log:
	$(COMPOSE) exec gfminio gfarm-s3-reset-brute-force-attack-log

shell:
	$(COMPOSE) exec gfminio bash

shell@copy_home:
	$(COMPOSE) exec copy_home bash

shell@revproxy:
	$(COMPOSE) exec revproxy bash

logs:
	$(COMPOSE) logs gfminio

logs-follow:
	$(COMPOSE) logs --follow gfminio

logs-time:
	$(COMPOSE) logs --timestamps gfminio

$(TARGET_LOGS): logs@%:
	$(COMPOSE) logs $*

$(TARGET_LOGS_FOLLOW): logs-follow@%:
	$(COMPOSE) logs --follow $*

$(TARGET_LOGS_TIME): logs-time@%:
	$(COMPOSE) logs --timestamps $*

ECHO_COMPOSE:
	@echo eval $(COMPOSE)
