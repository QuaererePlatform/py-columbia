__all__ = [
    'get_data_from_cc',
    'get_web_site_from_willamette',
    'get_web_page_body_from_cc',
    'web_page_exists',
]

import gzip
import io

from celery.utils.log import get_task_logger
import requests

from columbia.config import common as config

LOGGER = get_task_logger(__name__)


def get_web_site_from_willamette(web_site_key):
    # Until client code is more stable, use requests directly
    # web_site = self.willamette.v1.web_site.get(web_site_key)
    resp = requests.get(config.WILLAMETTE_URL + f'v1/web-site/{web_site_key}')
    if not resp.ok:
        LOGGER.error(f'Could not retrieve web_site data; '
                     f'_key={web_site_key}, reason: {resp.json()}')
        raise Exception  # FIXME
    return resp.json()


def get_data_from_cc(web_site_url, cc_index_key, index_url):
    params = {'url': f'{web_site_url}/*',
              'filter': '=status:200',
              'output': 'json'}
    LOGGER.info('Searching for website using CommonCrawl index'
                f' {cc_index_key}',
                extra={'cc_index_id': cc_index_key,
                       'index_url': index_url,
                       'web_site_url': web_site_url, })
    req = requests.get(index_url, params)
    if req.status_code != 200:
        LOGGER.error(f'Error searching {cc_index_key}',
                     stack_info=True,
                     extra={'params': params,
                            'index_url': index_url})
        raise Exception  # FIXME
    return req.text.splitlines()


def get_web_page_body_from_cc(cc_data):
    url = config.CC_DATA_URL_PREFIX + cc_data.filename
    file_end = cc_data.offset + cc_data.length - 1
    headers = {'Range': f'bytes={cc_data.offset}-{file_end}'}
    LOGGER.info()
    resp = requests.get(url, headers=headers)
    if not resp.ok:
        LOGGER.critical(f'Could not get data for web page: {cc_data}; '
                        f'{resp.status_code}, {resp.reason}')
        raise Exception  # FIXME
    web_page_data = gzip.GzipFile(
        fileobj=io.BytesIO(resp.content)).read().decode()
    _, _, html = web_page_data.strip().split('\r\n\r\n', 2)
    return html


def web_page_exists(cc_data):
    url = config.WILLAMETTE_URL + 'v1/web-page/find/'
    params = {
        'conditions': [
            'url==@url',
            'source_accounting.datetime_acquired==@date',
            'source_accounting.data_origin==@origin'
        ],
        'variables': {
            'url': cc_data.url,
            'date': cc_data.timestamp,
            'origin': 'common_crawl'
        },
    }
    resp = requests.get(url, params=params)
    if not resp.ok:
        LOGGER.critical(f'Could not query willamette for web page: {params}; '
                        f'{resp.status_code}, {resp.reason}')
        raise Exception  # FIXME
    if len(resp.json()['result']) == 0:
        return False
    else:
        return True
