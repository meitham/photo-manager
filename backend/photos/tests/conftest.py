import pytest
import mock
import os
from django.conf import settings


@pytest.fixture(scope='session')
def django_db_modify_db_settings(django_db_modify_db_settings,):
    os.environ['ENV'] = 'test'
    settings.DATABASES['default'] = {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     ':memory:'
    }


@pytest.fixture(autouse=True)
def mock_redis(request):
    mocks = ['classifiers.base_model.Lock', 'classifiers.style.model.Lock', 'classifiers.object.model.Lock']
    mocks = [mock.patch(x, mock.MagicMock()) for x in mocks]
    for m in mocks:
        m.start()
    yield
    for m in mocks:
        m.stop()

