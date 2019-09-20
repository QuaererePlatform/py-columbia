__all__ = ['get_collections', 'CCDataModelV1', 'CCIndexesModelV1',
           'CCScansModelV1']

import sys, inspect

from arango_orm import Collection

from .api_v1 import CCDataModel as CCDataModelV1
from .api_v1 import CCIndexesModel as CCIndexesModelV1
from .api_v1 import CCScansModel as CCScansModelV1


def _model_classes():
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], Collection) and cls[0] != 'Collection':
            yield cls[1]


def get_collections():
    for model in _model_classes():
        yield model
