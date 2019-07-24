import dotenv
import pytest

from columbia.app import create_app

dotenv.load_dotenv()


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    client = app.test_client()

    yield client
