import uuid

import requests

from threat9_test_bed.scenarios import HttpScenario
from threat9_test_bed.service_mocks.http_scenario_service import (
    HttpScenarioService,
)


def test_http_scenario_service_trash():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.TRASH) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.get(f"http://{target.host}:{target.port}"
                                f"/{uuid.uuid4().hex}")
        assert response.status_code == 200
        assert isinstance(response.content, bytes)
        assert len(response.content) > 0


def test_http_scenario_service_empty_response():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.EMPTY_RESPONSE) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.post(f"http://{target.host}:{target.port}"
                                 f"/{uuid.uuid4().hex}")
        assert response.status_code == 200
        assert isinstance(response.content, bytes)
        assert len(response.content) == 0


def test_http_scenario_service_error():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.ERROR) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.put(f"http://{target.host}:{target.port}"
                                f"/{uuid.uuid4().hex}")
        assert response.status_code == 500
        assert isinstance(response.content, bytes)
        assert len(response.content) > 0


def test_http_scenario_service_found():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.FOUND) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.patch(f"http://{target.host}:{target.port}"
                                  f"/{uuid.uuid4().hex}")
        assert response.status_code == 200
        assert response.content == b"OK"


def test_http_scenario_service_not_found():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.NOT_FOUND) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.post(f"http://{target.host}:{target.port}"
                                 f"/{uuid.uuid4().hex}")
        assert response.status_code == 404
        assert isinstance(response.content, bytes)
        assert len(response.content) > 0


def test_http_scenario_service_redirect():
    with HttpScenarioService("127.0.0.1", 8080,
                             scenario=HttpScenario.REDIRECT) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8080
        response = requests.get(f"http://{target.host}:{target.port}"
                                f"/{uuid.uuid4().hex}",
                                allow_redirects=False)
        assert response.status_code == 302


def test_http_scenario_service_random_port():
    with HttpScenarioService("127.0.0.1", 0,
                             scenario=HttpScenario.FOUND) as target:
        assert target.host == "127.0.0.1"
        assert target.port in range(1024, 65535 + 1)
        response = requests.post(f"http://{target.host}:{target.port}/foo")
        assert response.status_code == 200
        assert response.content == b"OK"
