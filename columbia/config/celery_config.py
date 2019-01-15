"""

http://docs.celeryproject.org/en/latest/userguide/configuration.html
"""

import os

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
