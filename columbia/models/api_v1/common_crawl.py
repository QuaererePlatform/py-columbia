__all__ = ['CCDataModel', 'CCIndexesModel', 'CCScansModel']

import logging

from arango_orm import Collection, relationship

from columbia_common.schemas.mixins import (
    CCDataFieldsMixin,
    CCIndexesFieldsMixin,
    CCScansFieldsMixin)

LOGGER = logging.getLogger(__name__)


class CCDataModel(CCDataFieldsMixin, Collection):
    __collection__ = 'CommonCrawlData'


class CCIndexesModel(CCIndexesFieldsMixin, Collection):
    __collection__ = 'CommonCrawlIndexes'


class CCScansModel(CCScansFieldsMixin, Collection):
    __collection__ = 'CommonCrawlScans'
    _index = [
        {'type': 'hash',
         'fields': ['web_site_key', 'cc_index_key'],
         'unique': True}]

    cc_index = relationship(CCIndexesModel, 'cc_index_key')
