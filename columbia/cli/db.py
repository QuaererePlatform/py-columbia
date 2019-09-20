__all__ = ['db_cli']

import logging
import sys
import time

from arango.exceptions import ServerConnectionError
from flask.cli import AppGroup
from requests.exceptions import ConnectionError

from columbia.app_util import get_db
from columbia.models import get_collections

LOGGER = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 30

db_cli = AppGroup('db')


@db_cli.command('init')
def init_db():
    db = get_db()
    ping = False
    time_out = DEFAULT_RETRY_TIMEOUT
    iter = 0
    while not ping and iter < time_out:
        try:
            ping = db.ping()
        except (ConnectionError, ServerConnectionError):
            LOGGER.debug(f'Ping failed, try {iter}')
            iter += 1
            time.sleep(1)
        LOGGER.info(f'Pinging db...; success: {ping}')
    if not ping:
        LOGGER.error('Could not connect to database')
        sys.exit(1)

    LOGGER.info('Initializing database')
    for collection in get_collections():
        if not db.has_collection(collection):
            LOGGER.info(f'Creating collection: {collection}')
            db.create_collection(collection)
