from logging import getLogger
import socketserver
from typing import Pattern, Union
from unittest import mock

logger = getLogger(__name__)


class TCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(
            self,
            server_address,
            request_handler_class,
            bind_and_activate=True,
    ):
        super().__init__(
            server_address, request_handler_class, bind_and_activate,
        )
        self.handlers = {}

    def get_handler(
            self,
            command: Union[bytes, Pattern[bytes]],
    ) -> mock.MagicMock:
        handler = self.handlers.get(command)
        if handler:
            return handler

        for pattern_key in self.handlers:
            if isinstance(pattern_key, Pattern):
                if pattern_key.match(command):
                    return self.handlers[pattern_key]

        handler = mock.MagicMock(name="default_handler")
        handler.return_value = b""

        return handler

    def get_command_mock(
            self,
            command: Union[bytes, Pattern[bytes]],
    ) -> mock.MagicMock:
        mocked_handler = mock.MagicMock(name=command)
        self.handlers[command] = mocked_handler
        return mocked_handler


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024)
            handler = self.server.get_handler(data)
            self.request.sendall(handler())
