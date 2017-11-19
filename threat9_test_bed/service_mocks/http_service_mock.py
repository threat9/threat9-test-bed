import logging
from unittest import mock

from flask import Flask

from .base_http_service import WSGIRefBasedHttpService

logger = logging.getLogger(__name__)


class HttpServiceMock(WSGIRefBasedHttpService):
    def __init__(self, host: str, port: int):
        super().__init__(host, port, Flask("target"))

    def get_route_mock(self, rule, **options):
        mocked_view = mock.MagicMock(name=rule, spec=lambda: None)
        self.app.add_url_rule(rule,
                              endpoint=rule,
                              view_func=mocked_view,
                              **options)
        logger.debug(f"{self} mock for '{rule}' has been added.")
        return mocked_view
