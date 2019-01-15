"""

https://connexion.readthedocs.io/en/latest/quickstart.html
"""
__all__ = ['app']

import connexion

app = connexion.FlaskApp(__name__)
app.add_api('columbia_api_v1.yaml')
