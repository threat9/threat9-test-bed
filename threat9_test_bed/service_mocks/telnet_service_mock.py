import logging
import threading
import typing
from unittest import mock

from ..scenarios import TelnetScenario
from ..telnet_service.protocol import TelnetServerClientProtocol
from ..telnet_service.telnet_server import TelnetServer
from .base_http_service import BaseService

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
        self.server.loop.stop()
        self.server_thread.join()

    def get_command_mock(self, command: str, handler: typing.Callable):
        command_mock = mock.Mock(name=command)
        self.protocol.add_command_handler(command, handler)
        return command_mock
