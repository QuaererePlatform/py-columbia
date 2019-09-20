__all__ = ['CCDataModel', 'CCIndexesModel', 'CCScansModel']

from datetime import datetime
import logging

from arango_orm import Collection, relationship

from columbia_common.schemas.api_v1.mixins import (
    CCDataFieldsMixin,
    CCIndexesFieldsMixin,
    CCScansFieldsMixin)

LOGGER = logging.getLogger(__name__)


class CCDataModel(CCDataFieldsMixin, Collection):
    __collection__ = 'CommonCrawlData'

    # @classmethod
    # def from_cc(cls, **data):
    #     key_rename_table = [
    #         ('urlkey', 'url_key'),
    #         ('mime-detected', 'mime_detected')
    #     ]
    #     value_conv_table = [
    #         ('timestamp', lambda x: datetime.strptime(x, '%Y%m%d%H%M%S')),
    #         ('length', int)
    #     ]
    #     for old_key, new_key in key_rename_table:
    #         if old_key not in data:
    #             continue
    #         data[new_key] = data.pop(old_key)
    #     for key, func in value_conv_table:
    #         if key in data:
    #             data[key] = func(data[key])
    #
    #     return cls(**data)


class CCIndexesModel(CCIndexesFieldsMixin, Collection):
    __collection__ = 'CommonCrawlIndexes'


class CCScansModel(CCScansFieldsMixin, Collection):
    __collection__ = 'CommonCrawlScans'
    _index = [
        {'type': 'hash',
         'fields': ['web_site_key', 'cc_index_key'],
         'unique': True}]

    cc_index = relationship(CCIndexesModel, 'cc_index_key')
