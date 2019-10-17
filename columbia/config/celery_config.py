"""

http://docs.celeryproject.org/en/latest/userguide/configuration.html
"""

import os

from .common import (
    ARANGODB_CLUSTER, ARANGODB_DATABASE, ARANGODB_HOST,
    ARANGODB_HOST_POOL, ARANGODB_PASSWORD, ARANGODB_USER, CC_COLL_INFO_URL,
    CC_DATA_URL_PREFIX, COLUMBIA_URL_PREFIX, WILLAMETTE_URL)
from .task_schedules import *

broker_host = os.environ.get('CELERY_BROKER_HOST', 'localhost')
broker_port = os.environ.get('CELERY_BROKER_PORT', '5672')
broker_auth = os.environ.get('CELERY_BROKER_AUTH', 'guest:guest')

result_host = os.environ.get('CELERY_RESULT_HOST', 'localhost')
result_port = os.environ.get('CELERY_RESULT_PORT', '6379')
result_auth = os.environ.get('CELERY_RESULT_AUTH', ':')
result_db_num = os.environ.get('CELERY_RESULT_DB_NUM', '0')

broker_url = f'amqp://{broker_host}'
result_backend = f'redis://{result_host}'

beat_schedule = {
    'monthly_cc_index_info_update': update_cc_index_info
}

arangodb_config = {'ARANGODB_CLUSTER': ARANGODB_CLUSTER,
                   'ARANGODB_DATABASE': ARANGODB_DATABASE,
                   'ARANGODB_HOST': ARANGODB_HOST,
                   'ARANGODB_HOST_POOL': ARANGODB_HOST_POOL,
                   'ARANGODB_PASSWORD': ARANGODB_PASSWORD,
                   'ARANGODB_USER': ARANGODB_USER}

cc_config = {'CC_COLL_INFO_URL': CC_COLL_INFO_URL,
             'CC_DATA_URL_PREFIX': CC_DATA_URL_PREFIX}

columbia_config = {'COLUMBIA_URL': COLUMBIA_URL_PREFIX + '/api/'}

willamette_config = {'WILLAMETTE_URL': WILLAMETTE_URL}
