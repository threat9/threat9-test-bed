from telnetlib import Telnet
from unittest.mock import MagicMock
import uuid

from threat9_test_bed.scenarios import TelnetScenario
from threat9_test_bed.service_mocks.telnet_service_mock import (
    TelnetServiceMock,
)


def test_telnet_service_mock_not_authorized():
    with TelnetServiceMock("127.0.0.1", 8023,
                           scenario=TelnetScenario.NOT_AUTHORIZED) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8023
        mock = target.get_command_mock("foo")
        mock.return_value = "bar"
        assert isinstance(mock, MagicMock)
        tn = Telnet(target.host, target.port, timeout=1.0)

        tn.expect([b"Login: ", b"login: "], 1.0)
        tn.write(b"admin" + b"\r\n")

        tn.expect([b"Password: ", b"password"], 1.0)
        tn.write(b"admin" + b"\r\n")

        _, match_object, _ = tn.expect([b"Login incorrect"], 1.0)
        assert match_object
        tn.close()


def test_telnet_service_mock_generic():
    with TelnetServiceMock("127.0.0.1", 8023,
                           scenario=TelnetScenario.GENERIC) as target:
        assert target.host == "127.0.0.1"
        assert target.port == 8023
        mock = target.get_command_mock("foo")
        mock.return_value = "bar"
        assert isinstance(mock, MagicMock)
        tn = Telnet(target.host, target.port, timeout=1.0)

        tn.expect([b"Login: ", b"login: "], 1.0)
        tn.write(b"admin" + b"\r\n")

        tn.expect([b"Password: ", b"password"], 1.0)
        tn.write(b"admin" + b"\r\n")

        tn.expect([b"admin@target:~\$"], 1.0)
        tn.write(b"foo" + b"\r\n")
        _, match_object, _ = tn.expect([b"bar"], 1.0)
        assert match_object
        tn.close()


def test_telnet_service_mock_authorized():
    with TelnetServiceMock("127.0.0.1", 0,
                           scenario=TelnetScenario.AUTHORIZED) as target:
        assert target.host == "127.0.0.1"
        assert target.port in range(1024, 65535 + 1)
        mock = target.get_command_mock("foo")
        mock.return_value = "bar"
        assert isinstance(mock, MagicMock)
        tn = Telnet(target.host, target.port, timeout=1.0)

        login = uuid.uuid4().hex.encode()
        tn.expect([b"Login: ", b"login: "], 1.0)
        tn.write(login + b"\r\n")

        password = uuid.uuid4().hex.encode()
        tn.expect([b"Password: ", b"password"], 1.0)
        tn.write(password + b"\r\n")

        tn.expect([login + b"@target:~\$"], 1.0)
        tn.write(b"foo" + b"\r\n")
        _, match_object, _ = tn.expect([b"bar"], 1.0)
        assert match_object
        tn.close()


def test_telnet_service_mock_add_credentials():
    with TelnetServiceMock("127.0.0.1", 8023,
                           scenario=TelnetScenario.GENERIC) as target:
        login = uuid.uuid4().hex.encode()
        password = uuid.uuid4().hex.encode()

        assert target.host == "127.0.0.1"
        assert target.port == 8023

        tn = Telnet(target.host, target.port, timeout=1.0)

        tn.expect([b"Login: ", b"login: "], 1.0)
        tn.write(login + b"\r\n")

        tn.expect([b"Password: ", b"password"], 1.0)
        tn.write(password + b"\r\n")

        _, match_object, _ = tn.expect([b"Login incorrect"], 1.0)
        assert match_object

        target.add_credentials(login.decode(), password.decode())

        tn.expect([b"Login: ", b"login: "], 1.0)
        tn.write(login + b"\r\n")

        tn.expect([b"Password: ", b"password"], 1.0)
        tn.write(password + b"\r\n")

        _, match_object, foo = tn.expect([login + b"@target:~\$"], 1.0)

        assert match_object, foo.decode()
        tn.close()


def test_telnet_service_mock_add_banner():
    with TelnetServiceMock("127.0.0.1", 8023,
                           scenario=TelnetScenario.GENERIC) as target:
        banner = b"Scoobeedoobeedoo where are you?"
        target.add_banner(banner)

        assert target.host == "127.0.0.1"
        assert target.port == 8023

        tn = Telnet(target.host, target.port, timeout=1.0)

        _, match_object, _ = tn.expect([banner], 1.0)
        assert match_object

        _, match_object, foo = tn.expect([b"Login: ", b"login: "], 1.0)
        assert match_object, foo.decode()
        tn.close()
