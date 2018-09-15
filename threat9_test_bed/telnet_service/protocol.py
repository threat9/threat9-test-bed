import asyncio
import logging
import typing

from faker import Faker

from threat9_test_bed.scenarios import TelnetScenario

logger = logging.getLogger(__name__)
faker = Faker()


def authorized(func):
    def _wrapper(self, data):
        message = data.decode().strip()
        if not self.authorized:
            if not self.login:
                self.login = message
                self.transport.write(b"Password: ")
                return
            else:
                self.password = message

            if (self.login, self.password) in self.creds:
                self.authorized = True
                self.transport.write(self.prompt.encode())
            else:
                self.transport.write(b"\r\nLogin incorrect\r\ntarget login: ")
                self.login = None
                self.password = None
            return
        else:
            func(self, data)

    return _wrapper


class GreedyList(list):
    def __contains__(self, item):
        return True


class TelnetServerClientProtocol(asyncio.Protocol):
    def __init__(self, scenario: TelnetScenario):
        self.transport = None
        self.remote_address = None
        self.scenario = scenario

        self.login = None
        self.password = None
        self.authorized = False

        self.banner = b""
        self._command_mocks = {}
        self._creds = [
            ("admin", "admin"),
            ("kocia", "dupa"),
        ]

    @property
    def creds(self):
        if self.scenario is TelnetScenario.NOT_AUTHORIZED:
            return []
        elif self.scenario is TelnetScenario.AUTHORIZED:
            return GreedyList()
        elif self.scenario is TelnetScenario.GENERIC:
            return self._creds

    @property
    def prompt(self):
        return f"{self.login}@target:~$ "

    def connection_made(self, transport: asyncio.Transport):
        self.remote_address = transport.get_extra_info("peername")
        logger.debug(f"Connection from {self.remote_address}")
        self.transport = transport
        if self.banner:
            self.transport.write(self.banner + b"\r\n")
        self.transport.write(b"Login: ")

    def _get_handler(
            self,
            command: typing.Union[str, typing.Pattern[str]],
    ) -> typing.Callable:

        handler = self._command_mocks.get(command)
        if handler:
            return handler

        for pattern_key in self._command_mocks:
            if isinstance(pattern_key, typing.Pattern):
                if pattern_key.match(command):
                    return self._command_mocks[pattern_key]

        return faker.paragraph

    @authorized
    def data_received(self, data: bytes):
        logger.debug(f"{self.remote_address} send: {data}")
        command = data.decode().strip()
        handler = self._get_handler(command)
        self.transport.write(
            f"{handler()}\r\n"f"{self.prompt}".encode()
        )

    def add_command_handler(self, command: str, handler: typing.Callable):
        self._command_mocks[command] = handler

    def add_credentials(self, login: str, password: str):
        self._creds.append((login, password))

    def add_banner(self, banner: bytes):
        self.banner = banner
