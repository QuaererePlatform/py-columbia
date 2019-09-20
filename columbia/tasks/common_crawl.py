__all__ = ['start_scan', 'update_all_cc_data', 'update_cc_index_info']

import json

from celery.utils.log import get_task_logger
from columbia_common.schemas.api_v1 import CCIndexesSchema
import requests

from columbia.config import common as config
from columbia.models.api_v1.common_crawl import CCDataModel, CCIndexesModel
from .app import app, ColumbiaTask

LOGGER = get_task_logger(__name__)


@app.task(base=ColumbiaTask, bind=True)
def start_scan(self, web_site_key, cc_index_key):
    # TODO: Let's figure out how to rate limit things...
    # TODO: Maybe even figure out how to do smaller chunk tracking for resuming

    web_site = self.willamette.v1.web_site.get(web_site_key)
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
            cc_data = CCDataModel(record)
            self.db_conn.add(cc_data)
        LOGGER.debug(f'Finished with {cc_index_key}')
    else:
        LOGGER.error(f'Error searching {cc_index_key}',
                     stack_info=True,
                     extra={'params': params,
                            'index_url': index_url})


@app.task(base=ColumbiaTask, bind=True)
def update_all_cc_data(self):
    web_sites = self.willamette.v1.web_site.all()
    sub_tasks = []
    for web_site in web_sites:
        for index_key in self.db_conn.query(CCIndexesModel).returns('_key').all():
            sub_tasks.append((web_site['_key'], index_key))
    return sub_tasks



@app.task(base=ColumbiaTask, bind=True)
def update_cc_index_info(self):
    LOGGER.info(f'Retrieving {config.CC_COLL_INFO_URL}')
    resp = requests.get(config.CC_COLL_INFO_URL)
    if resp.status_code == 200:
        schema = CCIndexesSchema()
        data = schema.load(resp.json(), many=True)
        if len(data.errors) > 0:
            LOGGER.error(f'Errors from unmarshal: {data.errors}')
            raise Exception
        for record in data.data:
            cc_index = CCIndexesModel(**record)
            self.db_conn.add(cc_index)
    else:
        LOGGER.error(f'Error {resp.status_code} retrieving'
                     f' {config.CC_COLL_INFO_URL}')
        raise Exception
