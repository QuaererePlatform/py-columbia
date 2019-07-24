__all__ = ['app', 'ColumbiaTask']

from celery import Celery, Task
from columbia_client import ColumbiaClient
from willamette_client import WillametteClient

from columbia.config.celery_config import (columbia_config, willamette_config)


class ColumbiaTask(Task):
    _columbia = None
    _willamette = None

    def __init__(self):
        self.columbia_config = columbia_config
        self.willamette_config = willamette_config

    @property
    def columbia(self):
        if self._columbia is None:
            self._columbia = ColumbiaClient(
                self.columbia_config['COLUMBIA_URL'])
        return self._columbia

    @property
    def willamette(self):
        if self._willamette is None:
            self._willamette = WillametteClient(
                self.willamette_config['WILLAMETTE_URL'])
        return self._willamette


app = Celery(__name__)
app.config_from_object('columbia.config.celery_config')
