import logging
import threading
from unittest import mock
from wsgiref.simple_server import make_server

from flask import Flask

from .base_http_service import BaseHttpService

logger = logging.getLogger(__name__)


class HttpServiceMock(BaseHttpService):
    def __init__(self, host: str, port: int):
        super().__init__(host, port, Flask("target"))
        self.server = make_server(self.host, self.port, self.app)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def get_route_mock(self, rule, **options):
        mocked_view = mock.MagicMock(name=rule, spec=lambda: None)
        self.app.add_url_rule(rule,
                              endpoint=rule,
                              view_func=mocked_view,
                              **options)
        logger.debug(f"{self} mock for '{rule}' has been added.")
        return mocked_view
