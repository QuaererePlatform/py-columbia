__all__ = ['ARANGODB_CLUSTER', 'ARANGODB_DATABASE', 'ARANGODB_HOST',
           'ARANGODB_HOST_POOL', 'ARANGODB_PASSWORD', 'ARANGODB_USER',
           'CC_COLL_INFO_URL', 'CC_DATA_URL_PREFIX', 'COLUMBIA_URL_PREFIX',
           'WILLAMETTE_URL']

import os

CC_COLL_INFO_URL = 'https://index.commoncrawl.org/collinfo.json'
CC_DATA_URL_PREFIX = 'https://commoncrawl.s3.amazonaws.com/'
WILLAMETTE_URL = os.environ.get("WILLAMETTE_URL",
                                'http://willamette.quaerere.local:5000/api/')
COLUMBIA_URL_PREFIX = os.environ.get(
    "COLUMBIA_URL_PREFIX",
    'http://columbia.quaerere.local:5000'
)
ARANGODB_USER = os.environ.get("ARANGODB_USER", default=None)
if not ARANGODB_USER:
    raise ValueError("Must set ARANGODB_USER environment variable")
ARANGODB_PASSWORD = os.environ.get("ARANGODB_PASSWORD", default=None)
if not ARANGODB_PASSWORD:
    raise ValueError("Must set ARANGODB_PASSWORD environment variable")
ARANGODB_DATABASE = os.environ.get("ARANGODB_DATABASE", default='quaerere')
ARANGODB_HOST = os.environ.get("ARANGODB_HOST", default=None)
if ARANGODB_HOST:
    protocol, host, port = ARANGODB_HOST.split(':')
    ARANGODB_HOST = (protocol, host.strip('//'), int(port))
else:
    ARANGODB_HOST = ('http', '127.0.0.1', 8529)
ARANGODB_CLUSTER = os.environ.get("ARANGODB_CLUSTER", default=False)
ARANGODB_HOST_POOL = None
if ARANGODB_CLUSTER and ARANGODB_CLUSTER.lower() == 'true':
    ARANGODB_CLUSTER = True
    ARANGODB_HOST_POOL = []
    for uri in os.environ.get("ARANGODB_HOST_POOL").split():
        protocol, host, port = uri.split(':')
        ARANGODB_HOST_POOL.append((protocol, host.strip('//'), int(port)))
