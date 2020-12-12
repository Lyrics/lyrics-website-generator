#!/usr/bin/make -f

# Makefile for Open Lyrics Database website generator

ASSETS_DIR = src/assets
SASS_OPTS = --style compressed
WWW_DIR=www
CSS_FILE = $(WWW_DIR)/s.css
FAVICON_FILE = favicon.ico
CONFIG_FILE = config.ini

build: $(CSS_FILE) $(FAVICON_FILE) $(CONFIG_FILE)
	@cd $(WWW_DIR) && \
        python3 ../build.py && \
        cp -r ../${ASSETS_DIR}/js . && \
        cp ../${ASSETS_DIR}/icons/artist.svg 2.svg && \
        cp ../${ASSETS_DIR}/icons/album.svg 3.svg && \
        cp ../${ASSETS_DIR}/icons/recording.svg 4.svg
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
        sassc ${SASS_OPTS} src/css/main.scss $(CSS_FILE) ||  echo -n ''

$(FAVICON_FILE): $(WWW_DIR)
	@cp ${ASSETS_DIR}/icons/$(FAVICON_FILE) $(WWW_DIR)/

serve: $(WWW_DIR)
	@cd $(WWW_DIR) && \
        echo "Starting local server at http://0.0.0.0:8100" && \
        python3 -m http.server 8100
.PHONY: serve

install-dependencies:
	pip3 install --user pystache simple-http-server
.PHONY: install-dependencies
