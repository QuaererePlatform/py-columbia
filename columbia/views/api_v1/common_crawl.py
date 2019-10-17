"""Views for handling common_crawl

"""
__all__ = ['CCDataView', 'CCIndexesView', 'CCScansView']

import logging

from columbia_common.schemas.api_v1 import (
    CCDataSchema, CCIndexesSchema, CCScansSchema)
from flask import jsonify, request
from flask_classful import route
from quaerere_base_flask.views.base import BaseView
from werkzeug.exceptions import MethodNotAllowed

from columbia.app_util import ArangoDBMixin
from columbia.models.api_v1 import (CCDataModel, CCIndexesModel, CCScansModel)
from columbia.tasks.common_crawl import (
    get_cc_data, update_all_web_site_cc_data, update_web_site_cc_data)

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

    def _post_create_callback(self, metadata):
        db_conn = self._get_db()
        cc_scan = db_conn.query(self._obj_model).by_key(metadata['_key'])
        res = get_cc_data.delay(cc_scan.web_site_key, cc_scan.cc_index_key)
        cc_scan.status = res.state
        cc_scan.task_id = res.id
        db_conn.update(cc_scan)

    def delete(self, key):
        raise MethodNotAllowed(
            valid_methods=[
                'HEAD',
                'OPTIONS',
                'GET',
                'POST',
            ]
        )

    @route('all-web-sites/', methods=['GET', 'OPTIONS'])
    def scan_all_web_sites(self):
        update_all_web_site_cc_data.delay()

    @route('web-site/', methods=['POST', 'OPTIONS'])
    def scan_web_site(self):
        valid_methods = ['POST', 'OPTIONS']
        if request.method not in valid_methods:
            raise MethodNotAllowed(valid_methods=valid_methods)
        try:
            web_site_key = request.json['web_site_key']
        except KeyError:
            errors = {'errors': 'Missing required key "web_site_key"'}
            return jsonify(errors), 400
        else:
            update_web_site_cc_data.delay(web_site_key)
