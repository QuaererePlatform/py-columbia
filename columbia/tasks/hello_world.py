__all__ = ['hello_world']

import logging

from .app import app

LOGGER = logging.getLogger(__name__)


@app.task
def hello_world():
    LOGGER.info('Hello World')
    return {'hello_world': True, 'remote': True}
