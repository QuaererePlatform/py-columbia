import logging

from celery import Celery

LOGGER = logging.getLogger(__name__)

app = Celery(__name__)
app.config_from_object('columbia.config.celery_config')
