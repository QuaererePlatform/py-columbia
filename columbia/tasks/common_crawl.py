import logging

import requests

from .app import app
from columbia import config
from columbia.db import common_crawl, web_sites

LOGGER = logging.getLogger(__name__)


@app.task
def update_cc_data():
    params = {'url': '', 'output': 'json'}
    for web_site_data in web_sites.get_all_websites():
        for index_url, index_id in common_crawl.get_cc_index_urls():



@app.task
def update_cc_index_info():
    req = requests.get(config.CC_COLL_INFO_URL)
    if req.status_code == 200:
        for record in req.json():
            common_crawl.update_index_info(record)
