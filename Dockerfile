FROM python:3.6-alpine
RUN apk update
RUN apk upgrade
RUN apk add gcc
RUN apk add musl-dev
RUN apk add yaml
RUN apk add yaml-dev
RUN mkdir /tmp/workdir
RUN mkdir /tmp/build
COPY columbia /tmp/build/columbia
COPY README.rst /tmp/build/
COPY MANIFEST.in /tmp/build/
COPY setup.* /tmp/build/
WORKDIR /tmp/build/
RUN python setup.py install
RUN apk del gcc
RUN apk del musl-dev
RUN apk del yaml-dev
COPY entrypoint.sh /usr/bin/
WORKDIR /tmp/workdir
ENTRYPOINT ["entrypoint.sh"]
