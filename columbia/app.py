"""

"""
__all__ = ['create_app']

from flask import Flask

from quaerere_base_flask.views import register_views

from .app_util import arangodb, register_logging
from .cli.db import db_cli


def create_app(*args, **kwargs):
    """Flask app factory

    :return: Flask app instance
    :rtype: Flask
    """
    app = Flask(__name__)
    app.logger.debug(f'Flask startup; args: {args}, kwargs: {kwargs}')
    register_logging(app)
    app.config.from_object('columbia.config.flask_config')
    arangodb.init_app(app)

    register_views(app, 'columbia.views.api_v1', 'v1')

    app.cli.add_command(db_cli)

    return app
