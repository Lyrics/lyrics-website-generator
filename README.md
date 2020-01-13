# lyrics-website

Lyrics website generator

The build script links against `lyrics.git`'s `database` directory
and outputs website files into `./www/`. The contents of that directory
then can be uploaded to a server.

## Requirements

    pip3 install pystache simple-http-server

## Build

    make clean all

## Run a local web-server

    make serve
