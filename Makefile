#!/usr/bin/make -f

ASSETS_DIR = src/assets
SASS_OPTS = --style compressed
WWW_DIR=www
CSS_FILE = $(WWW_DIR)/s.css
DB_DIR = $(WWW_DIR)/db
FAVICON_FILE = favicon.ico

all: build
.PHONY: all

clean:
	@rm -rf $(WWW_DIR)
.PHONY: clean

build: $(DB_DIR) $(CSS_FILE) $(FAVICON_FILE)
	@cd $(WWW_DIR) && \
    python3 ../build.py && \
    cp -r ../${ASSETS_DIR}/js . && \
    cp ../${ASSETS_DIR}/icons/artist.svg 1.svg && \
    cp ../${ASSETS_DIR}/icons/album.svg 2.svg && \
    cp ../${ASSETS_DIR}/icons/song.svg 3.svg
.PHONY: build

$(WWW_DIR):
	@mkdir $(WWW_DIR)

$(DB_DIR): $(WWW_DIR)
	@mkdir $(DB_DIR)

serve: $(WWW_DIR)
	@cd $(WWW_DIR) && \
    echo "Starting local server at http://0.0.0.0:8100" && \
    python3 -m http.server 8100
.PHONY: serve

$(CSS_FILE): $(WWW_DIR)
	@which sassc > /dev/null &2> /dev/null && \
    sassc ${SASS_OPTS} src/css/main.scss $(CSS_FILE) ||  echo -n ''

$(FAVICON_FILE): $(WWW_DIR)
	@cp ${ASSETS_DIR}/icons/$(FAVICON_FILE) $(WWW_DIR)/
