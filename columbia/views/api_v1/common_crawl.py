"""Views for handling common_crawl

"""
__all__ = ['CCDataView', 'CCIndexesView', 'CCScansView']

import logging

from quaerere_base_flask.views.base import BaseView

from columbia.app_util import get_db
from columbia.models.api_v1 import (CCDataModel, CCIndexesModel, CCScansModel)
from columbia.tasks.common_crawl import start_scan
from columbia_common.schemas import (
    CCDataSchema, CCIndexesSchema, CCScansSchema)

LOGGER = logging.getLogger(__name__)


class CCDataView(BaseView):
    _get_db = get_db
    _obj_model = CCDataModel
    _obj_schema = CCDataSchema


class CCIndexesView(BaseView):
    _get_db = get_db
    _obj_model = CCIndexesModel
    _obj_schema = CCIndexesSchema


class CCScansView(BaseView):
    _get_db = get_db
    _obj_model = CCScansModel
    _obj_schema = CCScansSchema

    excluded_methods = ['_post_create_callback', 'create_task']

    def create_task(self, cc_scan_metadata):
        db_conn = get_db()
        cc_scan = db_conn.query(self._obj_model).by_key(
            cc_scan_metadata['_key'])
        web_site_url = cc_scan.web_site_url
        cc_index_key = cc_scan.cc_index_key
        res = start_scan.apply_async(args=(web_site_url, cc_index_key))
        cc_scan.task_id = res.id
        db_conn.update(cc_scan)

    _post_create_callback = create_task

    def delete(self, key):
        error = {'errors': 'Method Not Allowed'}
        return error, 405
