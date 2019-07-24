"""

http://flask.pocoo.org/docs/1.0/config/#configuring-from-files
"""

__all__ = ['ARANGODB_CLUSTER', 'ARANGODB_DATABASE', 'ARANGODB_HOST',
           'ARANGODB_HOST_POOL', 'ARANGODB_PASSWORD', 'ARANGODB_USER',
           'CC_COLL_INFO_URL', 'CC_DATA_URL_PREFIX', 'COLUMBIA_URL_PREFIX',
           'PREFERRED_URL_SCHEME', 'SECRET_KEY', 'WILLAMETTE_URL']

import os

from .common import (
    ARANGODB_CLUSTER, ARANGODB_DATABASE, ARANGODB_HOST,
    ARANGODB_HOST_POOL, ARANGODB_PASSWORD, ARANGODB_USER, CC_COLL_INFO_URL,
    CC_DATA_URL_PREFIX, COLUMBIA_URL_PREFIX, WILLAMETTE_URL)

PREFERRED_URL_SCHEME = os.environ.get("FLASK_PREFERRED_URL_SCHEME",
                                      default='http')
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", default=None)
if not SECRET_KEY:
    raise ValueError("Must set SECRET_KEY environment variable")
