import logging
from unittest import mock

from flask import Flask

from .base_http_service import WerkzeugBasedHttpService

logger = logging.getLogger(__name__)


class HttpServiceMock(WerkzeugBasedHttpService):
    def __init__(self, host: str, port: int, ssl=False):
        super().__init__(host, port, Flask("target"), ssl)

    def get_route_mock(self, rule, **options):
        mocked_view = mock.MagicMock(name=rule, spec=lambda: None)
        self.app.add_url_rule(rule,
                              endpoint=rule,
                              view_func=mocked_view,
                              **options)
        logger.debug(f"{self} mock for '{rule}' has been added.")
        return mocked_view
