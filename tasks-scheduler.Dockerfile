FROM python:3.6-alpine
RUN mkdir /tmp/workdir
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
COPY . /app
ENV PYTHONPATH /app
WORKDIR /tmp/workdir
CMD ["celery", "-A", "columbia.tasks", "beat", "-l", "info"]
