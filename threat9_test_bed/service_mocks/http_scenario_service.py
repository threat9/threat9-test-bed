import logging

from ..http_service.app import app
from ..scenarios import HttpScenario
from .base_http_service import GunicornBasedHttpService

logger = logging.getLogger(__name__)


class HttpScenarioService(GunicornBasedHttpService):
    def __init__(self, host: str, port: int, scenario: HttpScenario):
        app.config.update(SCENARIO=scenario)
        super().__init__(host, port, app)
