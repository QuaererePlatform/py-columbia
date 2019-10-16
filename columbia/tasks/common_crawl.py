__all__ = ['get_cc_data', 'update_cc_index_data']

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
from .app import app, ColumbiaTask

LOGGER = get_task_logger(__name__)


@app.task(base=ColumbiaTask, bind=True)
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
        unmarshall = CCDataSchema().load(json.loads(record))
        if len(unmarshall.errors) != 0:
            LOGGER.warning(f'Errors unmarshalling record: {unmarshall.errors}')
            continue
        record = unmarshall.data
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


@app.task(base=ColumbiaTask, bind=True)
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
