ARG python_version=3.7
ARG gunicorn_version=19.9.0

FROM python:${python_version}-alpine
ARG gunicorn_version
RUN mkdir /tmp/build /tmp/workdir
COPY . /tmp/build/
COPY entrypoint.sh /usr/bin/entrypoint.sh
WORKDIR /tmp/build/
RUN apk update && \
    apk upgrade && \
    apk add gcc git musl-dev yaml yaml-dev && \
    pip install "gunicorn[eventlet]>=${gunicorn_version}" && \
    python setup.py install && \
    apk del gcc musl-dev yaml-dev
WORKDIR /tmp/workdir
ENV FLASK_APP="columbia.app:create_app"
ENTRYPOINT ["entrypoint.sh"]
