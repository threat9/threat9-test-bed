# thread9-test-bed

## Installation
```bash
$ pip install git+https://github.com/threat9/threat9-test-bed.git
```

## Test utilities

### `HttpServiceMock`
`HttpServiceMock` is a `flask` application that allows adding `unittests.mock` 
as view functions. This gives us ability to setup dummy http services 
on demand for testing purposes.

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

## Services
### `http`
```bash
$ test-bed http
```
#### `http` scenarios
|Scenario 	        |   Behavior    |
|-------------------|---------------|
|`empty_response`   |   returns empty response with `200` status code                       |
|`trash`            |   returns 100 characters long gibberish with `200` status code        |
|`not_found`        |   returns `404` status code                                           |
|`found`            |   returns _OK_ with `200` status code                                 |
|`redirect`         |   redirects you with `302` status code                                |
|`timeout`          |   sleep the server for 1 hour which effectively times out the request |
|`error`            |   returns `500` status code                                           |

```bash
$ test-bed http --scenario trash
```

### `https`
```bash
$ test-bed https
```

#### `https` scenarios
|Scenario 	        |   Behavior    |
|-------------------|---------------|
|`empty_response`   |   returns empty response with `200` status code                       |
|`trash`            |   returns 100 characters long gibberish with `200` status code        |
|`not_found`        |   returns `404` status code                                           |
|`found`            |   returns _OK_ with `200` status code                                 |
|`redirect`         |   redirects you with `302` status code                                |
|`timeout`          |   sleep the server for 1 hour which effectively times out the request |
|`error`            |   returns `500` status code                                           |

```bash
$ test-bed https --scenario found
```

## Troubleshooting
> I can't start my `https` service on port 443 due to `PermissionError`

Running services on it's default port may need extra privileges thus 
prepending command with `sudo` should do the trick e.g.
```bash
$ sudo test-bed https --scenario trash --port 443
[2017-09-16 12:51:18,137: INFO/werkzeug]  * Running on https://127.0.0.1:443/ (Press CTRL+C to quit)
```
This solution can be applied to other services and it's default ports as well.