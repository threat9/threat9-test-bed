from unittest.mock import MagicMock

import requests

from threat9_test_bed.service_mocks.http_service_mock import HttpServiceMock


def test_http_service_mock():
    with HttpServiceMock("127.0.0.1", 8080) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        mock = target.get_route_mock("/foo", methods=["POST"])
        mock.return_value = "bar", 201
        assert isinstance(mock, MagicMock)
        response = requests.post(f"http://{target.host}:{target.port}/foo")
        assert response.status_code == 201
        assert response.content == b"bar"


def test_https_service_mock():
    with HttpServiceMock("127.0.0.1", 8080, ssl=True) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        mock = target.get_route_mock("/foo", methods=["POST"])
        mock.return_value = "bar", 201
        assert isinstance(mock, MagicMock)
        response = requests.post(f"https://{target.host}:{target.port}/foo",
                                 verify=False)
        assert response.status_code == 201
        assert response.content == b"bar"


def test_http_service_mock_random_port():
    with HttpServiceMock("127.0.0.1", 0) as target:
        assert target.host == "127.0.0.1"
        assert target.port in range(1024, 65535 + 1)
        mock = target.get_route_mock("/foo", methods=["POST"])
        mock.return_value = "bar", 201
        assert isinstance(mock, MagicMock)
        response = requests.post(f"http://{target.host}:{target.port}/foo",
                                 verify=False)
        assert response.status_code == 201
        assert response.content == b"bar"
