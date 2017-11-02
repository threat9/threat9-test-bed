import logging

from ..http_server import http_server
from .base_http_service import BaseHttpService

logger = logging.getLogger(__name__)


class HttpScenarioService(BaseHttpService):
    def __init__(self, host: str, port: int, scenario: str):
        http_server.config.update(SCENARIO=scenario)
        super().__init__(host, port, http_server)
