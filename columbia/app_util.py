from flask_arango_orm import ArangoORM
# from flask_marshmallow import Marshmallow

arangodb = ArangoORM()
# marshmallow = Marshmallow()


def get_db():
    return arangodb.connection
