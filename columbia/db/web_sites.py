import logging

from .client import q_db, WEB_SITES_COLLECTION

LOGGER = logging.getLogger(__name__)


def mark_url_as_fetched(index_id, url):
    web_sites = q_db.collection(WEB_SITES_COLLECTION)
    db_cur = web_sites.find({'url': url})
    if db_cur.count() > 1:
        LOGGER.error('Found more than one instance of url in database.',
                     extra={'url': url})
        return False
    data = db_cur.batch()[0]
    if 'cc_index_ids_polled' not in data:
        LOGGER.debug('Dataset does not have any cc_index_ids_polled',
                     extra={'url': url})
        data['cc_index_ids_polled'] = []
    LOGGER.info('Adding index_id to url as fetched',
                extra={'url': url, 'index_id': index_id})
    data['cc_index_ids_polled'].append(index_id)
    web_sites.update(data)
    return True


def get_all_web_sites():
    LOGGER.info('Getting all websites...')
    web_sites = q_db.collection(WEB_SITES_COLLECTION)
    for web_site in web_sites.all():
        LOGGER.debug(f'Emitting {web_site}')
        yield web_site
