FROM python:3.7-alpine
ARG develop
RUN mkdir /tmp/build /tmp/workdir
COPY . /tmp/build/
COPY entrypoint.sh /usr/bin/
WORKDIR /tmp/build/
RUN apk update && apk upgrade
RUN apk add gcc git musl-dev yaml yaml-dev
RUN pip install "gunicorn[eventlet]>=19.9.0"
RUN if [ "${develop}" == "true" ]; then pip install -U -r requirements-bleeding.txt; pip freeze; fi
RUN python setup.py install
RUN apk del gcc musl-dev yaml-dev
WORKDIR /tmp/workdir
ENV FLASK_APP="columbia.app:create_app"
ENTRYPOINT ["entrypoint.sh"]
