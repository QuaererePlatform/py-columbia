__all__ = ['update_cc_index_info']

from celery.schedules import crontab

update_cc_index_info = {
    'task': 'columbia.tasks.cc_index.update_cc_index_info',
    'schedule': crontab(day_of_month=1)
}
