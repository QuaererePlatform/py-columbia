import os

CC_COLL_INFO_URL = 'https://index.commoncrawl.org/collinfo.json'
CC_DATA_URL_PREFIX = 'https://commoncrawl.s3.amazonaws.com/'
COLUMBIA_API_HOST = os.environ.get('COLUMBIA_API_HOST', 'columbia')
COLUMBIA_API_URL = f'http://{COLUMBIA_API_HOST}/api/v1'