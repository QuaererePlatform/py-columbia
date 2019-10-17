__all__ = ['app', 'CCScanTask']

from arango import ArangoClient
from arango_orm import ConnectionPool, Database
from celery import Celery, Task
from celery.utils.log import get_task_logger
# from willamette_client import WillametteClient

from columbia.config.celery_config import willamette_config
from columbia.config import common as common_config
from columbia.models import CCScansModelV1

LOGGER = get_task_logger(__name__)


class CCScanTask(Task):
    _db_conn = None
    _willamette = None

    def __init__(self):
        self.willamette_config = willamette_config

    @property
    def db_conn(self):
        if self._db_conn is None:
            self._db_conn = get_db()
        return self._db_conn

    # Client disabled until more stable, using plain requests for now
    # @property
    # def willamette(self):
    #     if self._willamette is None:
    #         self._willamette = WillametteClient(
    #             self.willamette_config['WILLAMETTE_URL'])
    #     return self._willamette

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        LOGGER.info(f"after_return; status: {status}, retval: {retval}, "
                    f"task_id: {task_id}, args: {args}, kwargs: {kwargs}, "
                    f"einfo: {einfo}")
        task = self.db_conn.query(CCScansModelV1).filter("task_id==@task_id",
                                                         task_id=task_id).one()
        task.status = status
        self.db_conn.update(task)


def get_db():
    if common_config.ARANGODB_CLUSTER:
        hosts = []
        for protocol, host, port in common_config.ARANGODB_HOST_POOL:
            hosts.append(ArangoClient(protocol=protocol,
                                      host=host,
                                      port=port))
        return ConnectionPool(hosts,
                              dbname=common_config.ARANGODB_DATABASE,
                              password=common_config.ARANGODB_PASSWORD,
                              username=common_config.ARANGODB_USER)
    else:
        protocol, host, port = common_config.ARANGODB_HOST
        client = ArangoClient(protocol=protocol,
                              host=host,
                              port=port)
        return Database(client.db(name=common_config.ARANGODB_DATABASE,
                                  username=common_config.ARANGODB_USER,
                                  password=common_config.ARANGODB_PASSWORD))


app = Celery(__name__)
app.config_from_object('columbia.config.celery_config')
