__all__ = ['q_db', 'WEB_SITES_COLLECTION']

import os

import arango

WEB_SITES_COLLECTION = 'WebSites'

a_client = arango.ArangoClient()
q_db = a_client.db('quaerere',
                   os.getenv('ARANGODB_USER'),
                   os.getenv('ARANGODB_PASSWD'))
