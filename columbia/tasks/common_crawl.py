import logging
import json

import requests

from .app import app
from columbia import config
from columbia.db import common_crawl, web_sites

LOGGER = logging.getLogger(__name__)


@app.task
def update_cc_data():
    # TODO: Let's figure out how to rate limit things...
    # TODO: Maybe even figure out how to do smaller chunk tracking for resuming
    for web_site_data in web_sites.get_all_websites():
        web_site_url = web_site_data['url']
        for index_url, index_id in common_crawl.get_cc_index_urls():
            if index_id in web_site_data.get('cc_index_ids_polled', []):
                LOGGER.info(f'Already searched {index_id} for {web_site_url}')
                continue
            params = {'url': f'{web_site_url}/*',
                      'filter': '=status:200',
                      'output': 'json'}
            LOGGER.info(f'Searching for {web_site_url} in {index_id}')
            req = requests.get(index_url, params)
            if req.status_code == 200:
                for record in req.text.splitlines():
                    record = json.loads(record)
                    if record['status'] != '200':
                        # This is only done as a double-check
                        LOGGER.error('Not sure how we ended up here: '
                                     f'found {record} using {index_id} '
                                     f'with {params}')
                        continue
                    LOGGER.debug(f'Evaluating {record} for CommonCrawl data')
                    common_crawl.update_cc_data(record)
                LOGGER.debug(f'Finished with {index_id}, marking as fetched')
                web_sites.mark_url_as_fetched(index_id, web_site_data['url'])
            else:
                LOGGER.error(f'Error {req.status_code} searching {index_id} '
                             f'with {params}')


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
