import logging

from .client import q_db

LOGGER = logging.getLogger(__name__)

CC_INDEX_INFO = 'CommonCrawlIndexInfo'
CC_DATA = 'CommonCrawlData'


def update_index_info(record):
    cc_index_info = q_db.collection(CC_INDEX_INFO)
    LOGGER.debug(f'Evaluating {record} for insert')
    if not cc_index_info.has(record['id']):
        record['_key'] = record['id']
        LOGGER.info(f'Adding {record["id"]}')
        cc_index_info.insert(record)


def get_cc_index_urls():
    collection = q_db.collection(CC_INDEX_INFO)
    for record in collection.all():
        LOGGER.info(f'Emitting {record}...')
        yield record['cdx-api'], record['id']


def update_cc_data(record):
    cc_data = q_db.collection(CC_DATA)
    db_cur = cc_data.find({'urlkey': record['urlkey']})
    if db_cur.count() > 1:
        LOGGER.error('Found more than one instance of urlkey in database: '
                     f'{record["urlkey"]}')
        return False
    elif db_cur.count() == 0:
        LOGGER.info(f'No instance of {record} found, inserting')
        cc_data.insert(record)
    else:
        LOGGER.info(f'Found instance of {record}, checking timestamp')
        page_data = db_cur.batch()[0]
        if int(record['timestamp']) > int(page_data['timestamp']):
            LOGGER.info(f'Newer record given, '
                        f'updating {page_data} with {record}')
            record['_key'] = page_data['_key']
            cc_data.update(record)
