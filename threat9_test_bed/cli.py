import logging

import click

from .http_service.app import app
from .scenarios import HttpScenario, TelnetScenario
from .service_mocks.http_service_mock import WerkzeugBasedHttpService
from .telnet_service.protocol import TelnetServerClientProtocol
from .telnet_service.telnet_server import TelnetServer

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command("http")
@click.option("--port",
              default=8080,
              show_default=True,
              help="HTTP server port.")
@click.option("--scenario",
              required=True,
              type=click.Choice(HttpScenario.names()),
              help="HTTP server behaviour.")
def run_http_server(scenario, port):
    logger.debug("Starting `http` server...")
    app.config.update(
        SCENARIO=HttpScenario[scenario],
    )
    WerkzeugBasedHttpService(
        app=app,
        host=f"127.0.0.1",
        port=port,
    ).start()
    logger.debug(f"`http` server has been started on port {port}.")


@cli.command("https")
@click.option("--port",
              default=8443,
              show_default=True,
              help="HTTPS server port.")
@click.option("--scenario",
              required=True,
              type=click.Choice(HttpScenario.names()),
              help="HTTP server behaviour.")
def run_https_server(scenario, port):
    logger.debug("Starting `https` server...")
    app.config.update(
        SCENARIO=HttpScenario[scenario],
    )
    WerkzeugBasedHttpService(
        app=app,
        host=f"127.0.0.1",
        port=port,
        ssl=True,
    ).start()
    logger.debug(f"`https` server has been started on port {port}.")


@cli.command("telnet")
@click.option("--port",
              default=8023,
              show_default=True,
              help="Telnet server port.")
@click.option("--scenario",
              required=True,
              type=click.Choice(TelnetScenario.names()),
              help="Telnet server behaviour.")
def run_telnet_server(scenario, port):
    logger.debug("Starting `telnet` server...")
    TelnetServer(
        host="127.0.0.1",
        port=port,
        protocol=lambda: TelnetServerClientProtocol(TelnetScenario[scenario]),
    ).run()
    logger.debug(f"`telnet` server has been started on port {port}.")
