import os

import arango

a_client = arango.ArangoClient()
q_db = a_client.db('quaerere',
                   os.getenv('ARANGODB_USER'),
                   os.getenv('ARANGODB_PASSWD'))
