__all__ = [
    'get_cc_data',
    'update_all_web_site_cc_data',
    'update_cc_index_data',
    'update_web_site_cc_data',
]

import json

from arango import DocumentInsertError
from celery.utils.log import get_task_logger
import requests

from columbia_common.schemas.api_v1 import (
    CCDataSchema,
    CCScansSchema,
    CCIndexesSchema)

from columbia.config import common as config
from columbia.models.api_v1.common_crawl import (
    CCDataModel,
    CCScansModel,
    CCIndexesModel)
from .app import (
    app,
    CCScanTask,
    ColumbiaTask)
from .util import (
    get_data_from_cc,
    get_web_site_from_willamette,
    get_web_page_body_from_cc,
    web_page_exists)

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
    web_site = get_web_site_from_willamette(web_site_key)
    cc_index = self.db_conn.query(CCIndexesModel).by_key(cc_index_key)

    records = get_data_from_cc(web_site['url'], cc_index_key, cc_index.cdx_api)
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
    """

    :param self:
    :param cc_data_key:
    :param web_site_key:
    :return:
    """
    cc_data = self.db_conn.query(CCScansModel).by_key(cc_data_key)
    if not web_page_exists(cc_data):
        url = config.WILLAMETTE_URL + 'v1/web-page/'
        web_page_data = {
            'text': get_web_page_body_from_cc(cc_data),
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


@app.task(base=CCScanTask)
def update_all_web_site_cc_data():
    """

    :return:
    """
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
