import logging

from logstash_async.handler import AsynchronousLogstashHandler


def setup_logging(config):
    root_logger = logging.getLogger()
    if config.logging_level == 'DEBUG':
        root_logger.setLevel(logging.DEBUG)
    elif config.logging_level == 'INFO':
        root_logger.setLevel(logging.INFO)
    elif config.logging_level == 'WARNING':
        root_logger.setLevel(logging.WARNING)
    elif config.logging_level == 'ERROR':
        root_logger.setLevel(logging.ERROR)
    elif config.logging_level == 'CRITICAL':
        root_logger.setLevel(logging.CRITICAL)
    if config.external_logging:
        root_logger.addHandler(AsynchronousLogstashHandler(
            config.logging_host,
            config.logging_port,
            database_path=config.logging_local_db))
