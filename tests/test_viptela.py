import pytest
import requests_mock

try:
    import mock
except ImportError:
    from unittest import mock

from collections import namedtuple
from viptela.exceptions import LoginTimeoutError, LoginCredentialsError
from viptela.viptela import parse_http_success


@pytest.fixture
def fake_get_request():
    response = mock.Mock(status_code=200)
    response.request.method = 'GET'
    response.json.return_value = {}
    return response


def test_parse_http_success_raises_key_error(fake_get_request):
    with pytest.raises(KeyError):
        parse_http_success(fake_get_request())
