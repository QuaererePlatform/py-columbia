__all__ = [
    'get_cc_data',
    'update_all_web_site_cc_data',
    'update_cc_index_data',
    'update_web_site_cc_data',
]

import gzip
import io
import json

from arango import DocumentInsertError
from celery.utils.log import get_task_logger
from columbia_common.schemas.api_v1 import (
    CCDataSchema,
    CCScansSchema,
    CCIndexesSchema)
import requests

from columbia.config import common as config
from columbia.models.api_v1.common_crawl import (
    CCDataModel,
    CCScansModel,
    CCIndexesModel)
from .app import app, CCScanTask, ColumbiaTask

LOGGER = get_task_logger(__name__)





@app.task(base=CCScanTask, bind=True)
def get_cc_data(self, web_site_key, cc_index_key):
    """Scan a Common Crawl index for a web site

    This method gets bound to ColumbiaTask

    :param self: hide me
    :param web_site_key:
    :param cc_index_key:
    :return:
    """
    # TODO: Let's figure out how to rate limit things...
    # TODO: Maybe even figure out how to do smaller chunk tracking for resuming

    # Until client code is more stable, use requests directly
    # web_site = self.willamette.v1.web_site.get(web_site_key)
    resp = requests.get(config.WILLAMETTE_URL + f'v1/web-site/{web_site_key}')
    if not resp.ok:
        LOGGER.error(f'Could not retrieve web_site data; '
                     f'_key={web_site_key}, reason: {resp.json()}')
        raise Exception  # FIXME
    web_site = resp.json()
    cc_index = self.db_conn.query(CCIndexesModel).by_key(cc_index_key)

    index_url = cc_index.cdx_api
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
    if req.status_code != 200:
        LOGGER.error(f'Error searching {cc_index_key}',
                     stack_info=True,
                     extra={'params': params,
                            'index_url': index_url})
        raise Exception  # FIXME
    records = req.text.splitlines()
    LOGGER.info(f'Found {len(records)} records')
    for record in records:
        unmarshal = CCDataSchema().load(json.loads(record))
        if len(unmarshal.errors) != 0:
            LOGGER.warning(f'Errors unmarshalling record: {unmarshal.errors}')
            continue
        record = unmarshal.data
        LOGGER.debug('Inserting record for CommonCrawl data: '
                     f"{record['url_key']}", extra={'record': record})
        try:
            self.db_conn.add(CCDataModel(**record))
        except DocumentInsertError as err:
            if '[ERR 1210]' in err.message:
                LOGGER.debug(f'Record exists: {err.message}')
            else:
                raise err
    LOGGER.info(f'Finished with {cc_index_key}')


@app.task(base=ColumbiaTask, bind=True)
def download_web_page_data(self, cc_data_key, web_site_key):
    cc_data = self.db_conn.query(CCScansModel).by_key(cc_data_key)
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
    q_data = resp.json()
    if len(q_data['result']) == 0:
        url = config.WILLAMETTE_URL + 'v1/web-page/'
        web_page_data = {
            'text': html,
            'url': cc_data.url,
            'web_site_key': web_site_key,
            'source_accounting': {
                'datetime_acquired': cc_data.timestamp,
                'data_origin': 'common_crawl',
            }
        }
        resp = requests.post(url, json=web_page_data)
        if not resp.ok:
            LOGGER.critical(f'Could not save web page data: {web_page_data}; '
                            f'{resp.status_code}, {resp.reason}')
            raise Exception  # FIXME
    else:
        # This is temporary, we should figure out how to either do versions or
        #   add a timestamp field so we can track changes to the web page
        LOGGER.warning(f'Web page data exists, doing nothing')


@app.task(base=CCScanTask, bind=True)
def update_web_site_cc_data(self, web_site_key):
    """Gets web site data from all Common Crawl indexes

    This method gets bound to ColumbiaTask

    :param self: hide me
    :param web_site_key:
    :return:
    """
    scan_url = config.COLUMBIA_URL_PREFIX + '/api/v1/cc-scans/'
    scan_schema = CCScansSchema()
    for index in self.db_conn.query(CCIndexesModel).all():
        if self.db_conn.query(
                CCScansModel).filter("cc_index_key==@index",
                                     index=index._key
                                     ).filter("web_site_key==@web_site",
                                              web_site=web_site_key
                                              ).count() == 0:
            scan = scan_schema.dump({'web_site_key': web_site_key,
                                     'cc_index_key': index._key})
            resp = requests.post(scan_url, json=scan.data)
            if not resp.ok:
                err = f"Could not create scan; " \
                      f"web_site_key: {web_site_key}, " \
                      f"cc_index_key: {index._key}, " \
                      f"status_code: {resp.status_code}, " \
                      f"error_data: {resp.text}"
                LOGGER.warning(err)


@app.task(base=CCScanTask, bind=True)
def update_all_web_site_cc_data(self):
    scan_url = config.COLUMBIA_URL_PREFIX + '/api/v1/cc-scans/scan-web-site/'
    web_sites_url = config.WILLAMETTE_URL + 'v1/web-sites/'
    resp = requests.get(web_sites_url)
    if not resp.ok:
        raise Exception  # Fixme
    web_sites = resp.json()
    for web_site in web_sites:
        resp = requests.post(scan_url, json={'web_site_key': web_site['_key']})
        if not resp.ok:
            LOGGER.warning(
                f"Unable to create scan for web_site '{web_site['_key']}',"
                f' reason: status_code: {resp.status_code}, {resp.json()}')


@app.task(base=CCScanTask, bind=True)
def update_cc_index_data(self):
    """Gets Common Crawl index data

    This method gets bound to ColumbiaTask

    :param self: hide me
    :return:
    """
    LOGGER.info(f'Retrieving {config.CC_COLL_INFO_URL}')
    resp = requests.get(config.CC_COLL_INFO_URL)
    if resp.status_code != 200:
        LOGGER.error(f'Error {resp.status_code} retrieving'
                     f' {config.CC_COLL_INFO_URL}')
        raise Exception  # FIXME

    schema = CCIndexesSchema()
    data = schema.load(resp.json(), many=True)
    if len(data.errors) > 0:
        LOGGER.error(f'Errors from unmarshal: {data.errors}')
        raise Exception
    LOGGER.info(f'Found {len(data.data)} records')
    for record in data.data:
        cc_index = CCIndexesModel(**record)
        LOGGER.debug(f'Inserting values: {record}')
        self.db_conn.add(cc_index)
