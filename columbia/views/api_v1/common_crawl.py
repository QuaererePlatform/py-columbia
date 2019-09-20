"""Views for handling common_crawl

"""
__all__ = ['CCDataView', 'CCIndexesView', 'CCScansView']

import logging

from columbia_common.schemas.api_v1 import (
    CCDataSchema, CCIndexesSchema, CCScansSchema)
from quaerere_base_flask.views.base import BaseView

from columbia.app_util import ArangoDBMixin
from columbia.models.api_v1 import (CCDataModel, CCIndexesModel, CCScansModel)
from columbia.tasks.common_crawl import start_scan

LOGGER = logging.getLogger(__name__)

CCDataSchema.model_class = CCDataModel
CCIndexesSchema.model_class = CCIndexesModel
CCScansSchema.model_class = CCScansModel


class CCDataView(ArangoDBMixin, BaseView):
    _obj_model = CCDataModel
    _obj_schema = CCDataSchema


class CCIndexesView(ArangoDBMixin, BaseView):
    _obj_model = CCIndexesModel
    _obj_schema = CCIndexesSchema


class CCScansView(ArangoDBMixin, BaseView):
    _obj_model = CCScansModel
    _obj_schema = CCScansSchema

    def _post_create_callback(self, cc_scan_metadata):
        db_conn = self._get_db()
        cc_scan = db_conn.query(self._obj_model).by_key(
            cc_scan_metadata['_key'])
        web_site_url = cc_scan.web_site_url
        cc_index_key = cc_scan.cc_index_key
        res = start_scan.delay(web_site_url, cc_index_key)
        cc_scan.task_id = res.id
        db_conn.update(cc_scan)

    def delete(self, key):
        error = {'errors': 'Method Not Allowed'}
        return error, 405
