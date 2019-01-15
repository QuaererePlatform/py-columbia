import logging

from .client import q_db

LOGGER = logging.getLogger(__name__)

CC_INDEX_INFO = 'CommonCrawlIndexInfo'
CC_DATA = 'CommonCrawlData'


def update_index_info(record):
    cc_index_info = q_db.collection(CC_INDEX_INFO)
    if not cc_index_info.has(record['id']):
        record['_key'] = record['id']
        LOGGER.info(f'Adding {record["id"]}')
        cc_index_info.insert(record)


def get_cc_index_urls():
    collection = q_db.collection(CC_INDEX_INFO)
    for record in collection.all():
        yield record['cdx-api'], record['id']


def update_cc_data(record):
    record['_key'] = record['urlkey']
    cc_data = q_db.collection(CC_DATA)
    if not cc_data.has(record['urlkey']):
        cc_data.insert(record)
    else:
        page_data = cc_data.get(record['urlkey'])
        if int(record['timestamp']) > int(page_data['timestamp']):
            cc_data.update(record)
