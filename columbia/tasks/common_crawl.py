import logging
import json

import requests

from .app import app
from columbia import config
from columbia.db import common_crawl, web_sites

LOGGER = logging.getLogger(__name__)


@app.task
def get_common_crawl_data(web_site_url, cc_index_id):
    # TODO: Let's figure out how to rate limit things...
    # TODO: Maybe even figure out how to do smaller chunk tracking for resuming
    index_url = ''
    web_site_data = {}
    if cc_index_id in web_site_data.get('cc_index_ids_polled', []):
        LOGGER.info('Already searched url using this index.',
                    extra={'cc_index_id': cc_index_id,
                           'index_url': index_url,
                           'web_site_url': web_site_url, })
        return False
    params = {'url': f'{web_site_url}/*',
              'filter': '=status:200',
              'output': 'json'}
    LOGGER.info('Searching for website using CommonCrawl index'
                f' {cc_index_id}',
                extra={'cc_index_id': cc_index_id,
                       'index_url': index_url,
                       'web_site_url': web_site_url, })
    req = requests.get(index_url, params)
    if req.status_code == 200:
        for record in req.text.splitlines():
            record = json.loads(record)
            if record['status'] != '200':
                # This is only done as a double-check
                LOGGER.error('Not sure how we ended up here.',
                             stack_info=True,
                             extra={'record': record,
                                    'params': params,
                                    'index_url': index_url, })
                continue
            LOGGER.debug('Evaluating record for CommonCrawl data',
                         extra={'record': record})
            common_crawl.update_cc_data(record)
        LOGGER.debug(f'Finished with {cc_index_id}, marking as fetched')
        web_sites.mark_url_as_fetched(cc_index_id, web_site_data['url'])
    else:
        LOGGER.error(f'Error searching {cc_index_id}',
                     stack_info=True,
                     extra={'params': params,
                            'index_url': index_url})


@app.task
def update_all_cc_data():
    for web_site_data in web_sites.get_all_web_sites():
        web_site_url = web_site_data['url']
        for index_url, index_id in common_crawl.get_cc_index_urls():
            pass


@app.task
def update_cc_index_info():
    LOGGER.info(f'Retrieving {config.CC_COLL_INFO_URL}')
    req = requests.get(config.CC_COLL_INFO_URL)
    if req.status_code == 200:
        for record in req.json():
            common_crawl.update_index_info(record)
    else:
        LOGGER.error(f'Error {req.status_code} retrieving'
                     f' {config.CC_COLL_INFO_URL}')
