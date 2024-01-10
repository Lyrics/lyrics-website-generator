#!/usr/bin/make -f

# Makefile for Open Lyrics Database website generator

BUILD_DEST_DIR=www
CONFIG_FILE = config.ini
CSS_FILE = $(BUILD_DEST_DIR)/g.css
DOCKER ?= $(if $(shell docker -v 2> /dev/null),docker,podman)
DOCKER_IMAGE_TAG ?= lyrics/website-generator
SASS_OPTS = --style compressed
PORT ?= 8100

.DEFAULT_GOAL := help

all: build serve ## Build and serve using Docker
.PHONY: all

include Prebuild.mk

help: ## Show this helpful message
	@for ML in $(MAKEFILE_LIST); do \
		grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$ML | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'; \
	done
.PHONY: help

build: clean $(BUILD_DEST_DIR) $(CONFIG_FILE) lyrics-database ## Build and extract website files using Docker
	@$(DOCKER) build -t $(DOCKER_IMAGE_TAG) .
	@$(DOCKER) run --rm $(DOCKER_IMAGE_TAG) sh -c "tar -czf - $(BUILD_DEST_DIR)" | tar -xzf -
.PHONY: build

lyrics-database: ## Copy Open Lyrics Database files into current working directory
	@if [ -d ../lyrics-database.git ]; then \
		mkdir -p lyrics-database && cp -r ../lyrics-database.git/database ../lyrics-database.git/translations lyrics-database/; \
	else \
		git clone https://github.com/Lyrics/lyrics-database.git; \
	fi

BUILD: $(BUILD_DEST_DIR) $(CSS_FILE) $(CONFIG_FILE) lyrics-database ## Build website
	@cd $(BUILD_DEST_DIR) && \
		python3 ../website-generator.py
.PHONY: BUILD

$(CONFIG_FILE): ## Generate config file (if it doesn't already exist)
	cp config.def.ini $(CONFIG_FILE)

clean: ## Remove everything from build directory
# 	@cd $(BUILD_DEST_DIR) && rm -rf {,.[!.],..?}*
	@rm -rf $(BUILD_DEST_DIR)
	@rm -rf lyrics-database
.PHONY: clean

$(BUILD_DEST_DIR): ## Create empty build directory (if it doesn't already exist)
	@mkdir -p $(BUILD_DEST_DIR)

$(CSS_FILE): $(BUILD_DEST_DIR) ## Compile CSS file
	@which sassc > /dev/null &2> /dev/null && \
		sassc ${SASS_OPTS} src/styles/page.scss $(CSS_FILE) || echo -n ''

serve: $(BUILD_DEST_DIR) ## Serve website files using Docker
	$(DOCKER) run -it -v "`pwd`"/$(BUILD_DEST_DIR):/src/website-generator/$(BUILD_DEST_DIR) --rm -p $(PORT):$(PORT) $(DOCKER_IMAGE_TAG)
.PHONY: serve

SERVE: $(BUILD_DEST_DIR) ## Serve website files directly from filesystem
	@echo "Starting local server for contents of $(BUILD_DEST_DIR) ..." && \
		python3 -m http.server --directory $(BUILD_DEST_DIR) $(PORT)
.PHONY: SERVE

tunnel: ## Enter Docker shell
	@$(DOCKER) run -it --rm $(DOCKER_IMAGE_TAG) sh || true
.PHONY: tunnel
