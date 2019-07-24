FROM python:3.7-alpine
RUN apk update
RUN apk upgrade
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN mkdir /tmp/workdir
COPY test_data.yaml /tmp/workdir/
WORKDIR /tmp/workdir
COPY integration_runner.py /usr/bin/
ENTRYPOINT ["integration_runner.py"]