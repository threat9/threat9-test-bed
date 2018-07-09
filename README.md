# threat9-test-bed

## Installation
```bash
$ pip install git+https://github.com/threat9/threat9-test-bed.git
```

## Test utilities

### `HttpServiceMock`
`HttpServiceMock` is a `flask` application that allows for  adding 
`unittests.mock`  as view functions. This gives us ability to setup dummy 
http services on demand for testing purposes.

```python
from threat9_test_bed.service_mocks import HttpServiceMock

from foo import ExploitUnderTest


def test_exploit():
    with HttpServiceMock("localhost", 8080) as target: 
        cgi_mock = target.get_route_mock("/cgi-bin/cgiSrv.cgi",
                                         methods=["POST"])
        cgi_mock.return_value = 'foo status="doing" bar'
        check_mock = target.get_route_mock("/routersploit.check",
                                           methods=["GET", "POST"])
        check_mock.return_value = 'root'
    
        exploit = ExploitUnderTest(f'http://{target.host}', target.port)
        assert exploit.check() is True
        cgi_mock.assert_called_once()
        assert check_mock.call_count == 2
```
It is very convenient to use `py.test` library and it's fixture abilities. 
Such fixture will perform setup and teardown automatically before each test. 
All we have to do is to pass `target` as the test argument.
```python
import pytest
from threat9_test_bed.service_mocks import HttpServiceMock

from foo import ExploitUnderTest


@pytest.fixture
def target():
    with HttpServiceMock("localhost", 8080) as target_:
        yield target_


def test_exploit(target):
    cgi_mock = target.get_route_mock("/cgi-bin/cgiSrv.cgi",
                                     methods=["POST"])
    cgi_mock.return_value = 'foo status="doing" bar'
    check_mock = target.get_route_mock("/routersploit.check",
                                       methods=["GET", "POST"])
    check_mock.return_value = 'root'

    exploit = ExploitUnderTest(f'http://{target.host}', target.port)
    assert exploit.check() is True
    cgi_mock.assert_called_once()
    assert check_mock.call_count == 2
```
#### Adhoc SSL support
You can serve `HttpScenarioService` using adhoc SSL certificate by setting
`ssl` keyword argument to `True`:

```python
from threat9_test_bed.service_mocks import HttpServiceMock

@pytest.fixture
def trash_target():
    with HttpServiceMock("127.0.0.1", 0, ssl=True) as http_service:
        yield http_service
```

### `HttpScenarioService`
`HttpScenarioService` allows for creating test utilities using pre-defined
[scenarios](#http-scenarios)
```python
import pytest

from threat9_test_bed.scenarios import HttpScenario
from threat9_test_bed.service_mocks import HttpScenarioService


@pytest.fixture(scope="session")
def empty_target():
    with HttpScenarioService("127.0.0.1", 8081,
                             HttpScenario.EMPTY_RESPONSE) as http_service:
        yield http_service


@pytest.fixture(scope="session")
def trash_target():
    with HttpScenarioService("127.0.0.1", 8082,
                             HttpScenario.TRASH) as http_service:
        yield http_service

```

#### Adhoc SSL support
You can serve `HttpScenarioService` using adhoc SSL certificate by setting
`ssl` keyword argument to `True`:

```python
from threat9_test_bed.service_mocks import HttpScenarioService

@pytest.fixture(scope="session")
def trash_target():
    with HttpScenarioService("127.0.0.1", 8443, HttpScenario.TRASH, 
                             ssl=True) as http_service:
        yield http_service
```

### `TelnetServiceMock`
`TelnetServiceMock` allows for creating test utilities using pre-defined
[scenarios](#telnet-scenarios) as well as attaching `unittests.mock`
as command handlers. This gives us ability to setup dummy telnet service
on demand for testing purposes.
```python
from telnetlib import Telnet

import pytest

from threat9_test_bed.service_mocks.telnet_service_mock import TelnetServiceMock
from threat9_test_bed.scenarios import TelnetScenarios


@pytest.fixture
def generic_target():
    with TelnetServiceMock("127.0.0.1", 8023,
                           TelnetScenarios.AUTHORIZED) as telnet_service:
        yield telnet_service


def test_telnet(generic_target):
    command_mock = target.get_command_mock("scoobeedoobeedoo")
    command_mock.return_value = "Where are you?"

    tn = Telnet(target.host, target.port, timeout=5)
    tn.expect([b"Login: ", b"login: "], 5)
    tn.write(b"admin" + b"\r\n")

    tn.expect([b"Password: ", b"password"], 5)
    tn.write(b"admin" + b"\r\n")

    tn.expect([b"admin@target:~$"], 5)
    tn.write(b"scoobeedoobeedoo" + b"\r\n")
    _, match_object, _ = tn.expect([b"Where are you?"], 5)

    tn.close()

    assert match_object
```

### Random port
To avoid `port` collison during tests you can tell test utilities to set
it for you by passing `0`
```python
@pytest.fixture(scope="session")
def trash_target():
    with HttpScenarioService("127.0.0.1", 0,
                             HttpScenario.TRASH) as http_service:
        yield http_service
```

## Services
### `http`
```bash
$ test-bed http
```
#### `http` scenarios
|Scenario 	        |   Behavior    |
|-------------------|---------------|
|`EMPTY_RESPONSE`   |   returns empty response with `200` status code                       |
|`TRASH`            |   returns 100 characters long gibberish with `200` status code        |
|`NOT_FOUND`        |   returns `404` status code                                           |
|`FOUND`            |   returns _OK_ with `200` status code                                 |
|`REDIRECT`         |   redirects you with `302` status code                                |
|`TIMEOUT`          |   sleep the server for 1 hour which effectively times out the request |
|`ERROR`            |   returns `500` status code                                           |                                          |

```bash
$ test-bed http --scenario TRASH
```

### `https`
```bash
$ test-bed https
```

#### `https` scenarios
|Scenario 	        |   Behavior    |
|-------------------|---------------|
|`EMPTY_RESPONSE`   |   returns empty response with `200` status code                       |
|`TRASH`            |   returns 100 characters long gibberish with `200` status code        |
|`NOT_FOUND`        |   returns `404` status code                                           |
|`FOUND`            |   returns _OK_ with `200` status code                                 |
|`REDIRECT`         |   redirects you with `302` status code                                |
|`TIMEOUT`          |   sleep the server for 1 hour which effectively times out the request |
|`ERROR`            |   returns `500` status code                                           |

```bash
$ test-bed https --scenario FOUND
```

### `telnet`
After successful authorization elnet service responds with random
_Lorem ipsum..._ for every command
```bash
$ test-bed telnet
```
#### `telnet` scenarios
|Scenario 	        |   Behavior    |
|-------------------|---------------|
|`AUTHORIZED`       |   Any authorization attempt ends with success         |
|`NOT_AUTHORIZED`   |   Every authorization attempt ends with failure       |
|`GENERIC`          |   Authorization using `admin/admin` credentials       |
|`TIMEOUT`          |   Server hangs as soon as client has been connected   |

```bash
$ test-bed telnet --scenario GENERIC
```

## Troubleshooting
> I can't start my `https` service on port 443 due to `PermissionError`

Running services on it's default port may need extra privileges thus 
prepending command with `sudo` should do the trick e.g.
```bash
$ sudo test-bed https --scenario TRASH --port 443
[2017-09-16 12:51:18,137: INFO/werkzeug]  * Running on https://127.0.0.1:443/ (Press CTRL+C to quit)
```
This solution can be applied to other services and it's default ports as well.