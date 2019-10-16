__all__ = ['CCDataModel', 'CCIndexesModel', 'CCScansModel']

from arango_orm import Collection, relationship

from columbia_common.schemas.api_v1.mixins import (
    CCDataFieldsMixin,
    CCIndexesFieldsMixin,
    CCScansFieldsMixin)


class CCDataModel(CCDataFieldsMixin, Collection):
    __collection__ = 'CommonCrawlData'
    _index = [
        {'type': 'hash',
         'fields': ['timestamp', 'url_key'],
         'unique': True}]


class CCIndexesModel(CCIndexesFieldsMixin, Collection):
    __collection__ = 'CommonCrawlIndexes'


class CCScansModel(CCScansFieldsMixin, Collection):
    __collection__ = 'CommonCrawlScans'
    _index = [
        {'type': 'hash',
         'fields': ['web_site_key', 'cc_index_key'],
         'unique': True}]

    cc_index = relationship(CCIndexesModel, 'cc_index_key')
