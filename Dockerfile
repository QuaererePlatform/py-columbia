FROM python:3.7-alpine
RUN apk update && upgrade
RUN apk add gcc git musl-dev yaml yaml-dev
RUN mkdir /tmp/build /tmp/workdir
COPY columbia /tmp/build/columbia
COPY README.rst /tmp/build/
COPY LICENSE.txt /tmp/build/
COPY VERSION /tmp/build/
COPY setup.* /tmp/build/
WORKDIR /tmp/build/
RUN pip install "gunicorn[eventlet]>=19.9.0"
RUN python setup.py install
RUN apk del gcc musl-dev yaml-dev
COPY entrypoint.sh /usr/bin/
WORKDIR /tmp/workdir
ENTRYPOINT ["entrypoint.sh"]
