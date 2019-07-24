"""

"""
__all__ = ['create_app']

from flask import Flask

from quaerere_base_flask.views import register_views

from .app_util import arangodb  # , marshmallow
from .cli.db import db_cli


def create_app():
    app = Flask(__name__)
    app.config.from_object('columbia.config.flask_config')
    # marshmallow.init_app(app)
    arangodb.init_app(app)

    register_views(app, 'columbia.views.api_v1', 'v1')

    app.cli.add_command(db_cli)

    return app
