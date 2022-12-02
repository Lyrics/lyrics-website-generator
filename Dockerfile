FROM alpine:latest

RUN apk update && apk add gcc g++ make musl-dev python3 python3-dev py3-pip py3-wheel sassc

WORKDIR /src/website-generator

ADD Prebuild.mk requirements.txt ./

RUN make -f Prebuild.mk INSTALL_DEPENDENCIES

ADD . .

RUN make BUILD

CMD ["make", "SERVE"]
