import logging

from columbia.db.client import q_db, WEB_SITES_COLLECTION

LOGGER = logging.getLogger(__name__)


def url_downloaded_get(url, cc_index_id):
    web_sites = q_db.collection(WEB_SITES_COLLECTION)
    db_cur = web_sites.find({'url': url})
    if db_cur.count() > 1:
        LOGGER.error(f'Found more than one instance of url in database.',
                     extra={'url': url})
        return None, 500
    data = db_cur.batch()[0]
    if 'cc_index_ids_polled' not in data:
        LOGGER.debug('Dataset does not have any cc_index_ids_polled',
                     extra={'url': url})
        return {'url_downloaded': False}, 200
    elif cc_index_id not in data['cc_index_ids_polled']:
        LOGGER.debug('URL does not have data for this CC index',
                     extra={'url': url, 'cc_index_id': cc_index_id})
        return {'url_downloaded': False}, 200
    elif cc_index_id in data['cc_index_ids_polled']:
        LOGGER.debug('URL has data for this CC index',
                     extra={'url': url, 'cc_index_id': cc_index_id})
        return {'url_downloaded': True}, 200


def url_downloaded_post(url, cc_index_id):
    pass
