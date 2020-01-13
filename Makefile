#!/usr/bin/make -f

ASSETS_FILES = src/assets
CSS_FILE = www/s.css
SASS_OPTS = --style compressed

all: build

clean:
	@rm -rf www

build: www/db css
	@cd www && python3 ../build.py && cp -r ../${ASSETS_FILES}/* .

www:
	@mkdir www

www/db: www
	@mkdir www/db

serve: www
	@cd www/ && \
        echo "Starting local server at http://0.0.0.0:8100" && \
        python3 -m http.server 8100

css: www
	@which sassc > /dev/null &2> /dev/null && \
         sassc ${SASS_OPTS} src/css/main.scss $(CSS_FILE) \
         || echo -n ''

.PHONY: all clean build serve css
