#!/usr/bin/make -f

SASS_OPTS = --style compressed
CSS_FILE = www/s.css
ASSETS_FILES = src/assets


all: clean build

clean:
	rm -rf www

build: www css
	cd www && python ../build.py && cp -r ../${ASSETS_FILES}/* .

www:
	mkdir -p www/db

serve: www
	cd www/
	@echo "Starting local server at http://0.0.0.0:8100"
	@python -m SimpleHTTPServer 8100

css:
	@which sassc > /dev/null &2> /dev/null && \
         sassc ${SASS_OPTS} src/css/style.scss $(CSS_FILE) \
         || echo -n ''

.PHONY: all clean build serve css
