import logging

from .client import q_db

LOGGER = logging.getLogger(__name__)

COLLECTIONS = ['CommonCrawlData',
               'CommonCrawlIndexInfo', ]


def init_db():
    LOGGER.info('Initializing database')
    for collection in COLLECTIONS:
        if not q_db.has_collection(collection):
            LOGGER.info(f'Creating collection: {collection}')
            q_db.create_collection(collection)
