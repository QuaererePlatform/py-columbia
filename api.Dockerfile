FROM python:3.6-alpine
RUN mkdir /tmp/workdir
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY . /app
ENV PYTHONPATH /app
WORKDIR /tmp/workdir
ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "columbia.api:app"]
