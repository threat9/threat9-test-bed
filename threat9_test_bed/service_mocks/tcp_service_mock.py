from logging import getLogger
import re
import threading
from typing import Pattern, Union
from unittest import mock

from ..tcp_service.tcp_server import TCPHandler, TCPServer
from .base_service import BaseService

logger = getLogger(__name__)


class TCPServiceMock(BaseService):

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.server = TCPServer((self.host, self.port), TCPHandler, False)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.server.server_bind()
        self.server.server_activate()
        self.server_thread.start()

    def teardown(self):
        self.server.shutdown()
        self.server_thread.join()
        self.server.server_close()

    def get_command_mock(
            self,
            command: Union[bytes, Pattern[bytes]],
    ) -> mock.MagicMock:
        logger.debug(f"{self} mock for '{command}' has been added.")
        return self.server.get_command_mock(command)

    def get_command_mock_re(
            self,
            command: bytes,
            **kwargs,
    ):
        return self.get_command_mock(re.compile(command, **kwargs))
