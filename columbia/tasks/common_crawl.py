import json

from celery.utils.log import get_task_logger
import requests

from .app import app, ColumbiaTask
from columbia.config import common as config

LOGGER = get_task_logger(__name__)


@app.task(base=ColumbiaTask, bind=True)
def start_scan(self, web_site_key, cc_index_key):
    # TODO: Let's figure out how to rate limit things...
    # TODO: Maybe even figure out how to do smaller chunk tracking for resuming

    web_site = self.willamette.v1.web_site.get(web_site_key)
    cc_index = self.columbia.v1.cc_indexes.get(cc_index_key)


    index_url = cc_index['cdx_api']
    web_site_url = web_site['url']

    params = {'url': f'{web_site_url}/*',
              'filter': '=status:200',
              'output': 'json'}
    LOGGER.info('Searching for website using CommonCrawl index'
                f' {cc_index_key}',
                extra={'cc_index_id': cc_index_key,
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
            # common_crawl.update_cc_data(record)
        LOGGER.debug(f'Finished with {cc_index_key}, marking as fetched')
        # web_sites.mark_url_as_fetched(cc_index_id, web_site_data['url'])
    else:
        LOGGER.error(f'Error searching {cc_index_key}',
                     stack_info=True,
                     extra={'params': params,
                            'index_url': index_url})


@app.task
def update_all_cc_data():
    resp = requests.get(config.WILLAMETTE_URL + 'v1/web-sites/')
    if resp.status_code != 200:
        raise Exception
    web_sites = resp.json()
    for web_site_data in web_sites:
        web_site_url = web_site_data['url']
        for index_url, index_id in common_crawl.get_cc_index_urls():
            pass


@app.task
def update_cc_index_info():
    LOGGER.info(f'Retrieving {config.CC_COLL_INFO_URL}')
    resp = requests.get(config.CC_COLL_INFO_URL)
    if resp.status_code == 200:
        for record in resp.json():
            common_crawl.update_index_info(record)
    else:
        LOGGER.error(f'Error {resp.status_code} retrieving'
                     f' {config.CC_COLL_INFO_URL}')
