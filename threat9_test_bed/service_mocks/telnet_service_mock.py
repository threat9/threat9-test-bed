import logging
import re
import threading
import typing
from unittest import mock

from ..scenarios import TelnetScenario
from ..telnet_service.protocol import TelnetServerClientProtocol
from ..telnet_service.telnet_server import TelnetServer
from .base_service import BaseService

logger = logging.getLogger(__name__)


class TelnetServiceMock(BaseService):
    def __init__(self,
                 host: str, port: int,
                 scenario: TelnetScenario=TelnetScenario.AUTHORIZED):
        super().__init__(host, port)
        self.protocol = TelnetServerClientProtocol(scenario)
        self.server = TelnetServer(
            self.host,
            self.port,
            lambda: self.protocol
        )
        self.server_thread = threading.Thread(target=self.server.run)

    def start(self):
        self.server_thread.start()

    def teardown(self):
        self.server.loop.call_soon_threadsafe(self.server.loop.stop)
        self.server_thread.join()

    def get_command_mock(
            self,
            command: typing.Union[str, typing.Pattern[str]],
    ):
        command_mock = mock.MagicMock(name=command)
        self.protocol.add_command_handler(command, command_mock)
        return command_mock

    def get_command_mock_re(
            self,
            command: str,
            **kwargs,
    ):
        return self.get_command_mock(re.compile(command, **kwargs))

    def add_credentials(self, login: str, password: str):
        """ Add custom credentials pair. """
        self.protocol.add_credentials(login, password)

    def add_banner(self, banner: bytes):
        """ Add welcoming banner after connection. """
        self.protocol.add_banner(banner)
