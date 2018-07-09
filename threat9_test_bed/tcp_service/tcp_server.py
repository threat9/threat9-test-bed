from logging import getLogger
import socketserver
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

    def get_command_mock(self, command: bytes) -> mock.Mock:
        mocked_handler = mock.MagicMock(name=command)
        self.handlers[command] = mocked_handler
        return mocked_handler


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(1024)
            handler = self.server.handlers.get(data, lambda: b"")
            self.request.sendall(handler())
