import logging

import click
from threat9_test_bed.http_server import http_server, HTTP_SCENARIOS

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command('http')
@click.option('--port',
              default=8080,
              show_default=True,
              help="HTTP server port.")
@click.option('--scenario',
              required=True,
              type=click.Choice(HTTP_SCENARIOS.keys()),
              help='HTTP server behaviour.')
def run_http_server(scenario, port):
    logger.debug("Starting `http` server...")
    http_server.config.update(
        SCENARIO=scenario,
    )
    http_server.run(port=port)
    logger.debug(f"`http` server has been started on port {port}.")


@cli.command('https')
@click.option('--port',
              default=8443,
              show_default=True,
              help="HTTPS server port.")
@click.option('--scenario',
              required=True,
              type=click.Choice(HTTP_SCENARIOS.keys()),
              help='HTTP server behaviour.')
def run_https_server(scenario, port):
    logger.debug("Starting `https` server...")
    http_server.config.update(
        SCENARIO=scenario,
    )
    http_server.run(port=port, ssl_context='adhoc')
    logger.debug(f"`https` server has been started on port {port}.")
