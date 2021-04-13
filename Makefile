#!/usr/bin/make -f

# Makefile for Open Lyrics Database website generator

ASSETS_DIR = src/assets
SASS_OPTS = --style compressed
WWW_DIR=www
CSS_FILE = $(WWW_DIR)/s.css
CONFIG_FILE = config.ini

all: build

build: $(CSS_FILE) $(CONFIG_FILE)
	@cd $(WWW_DIR) && \
        python3 ../website-generator.py
.PHONY: build

$(CONFIG_FILE):
	cp config.def.ini $(CONFIG_FILE)

clean:
	@rm -rf $(WWW_DIR)
.PHONY: clean

$(WWW_DIR):
	@mkdir $(WWW_DIR)

$(CSS_FILE): $(WWW_DIR)
	@which sassc > /dev/null &2> /dev/null && \
        sassc ${SASS_OPTS} src/sass/page.scss $(CSS_FILE) ||  echo -n ''

serve: $(WWW_DIR)
	@cd $(WWW_DIR) && \
        echo "Starting local server at http://0.0.0.0:8100" && \
        python3 -m http.server 8100
.PHONY: serve
