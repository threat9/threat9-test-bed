import logging

import click

from .app import app
from .gunicorn_server import GunicornServer
from .scenarios import HttpScenario

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
              type=click.Choice(HttpScenario.names()),
              help='HTTP server behaviour.')
def run_http_server(scenario, port):
    logger.debug("Starting `http` server...")
    app.config.update(
        SCENARIO=HttpScenario[scenario],
    )
    GunicornServer(
        app=app,
        bind=f"127.0.0.1:{port}",
        worker_class="gthread",
        threads=8,
        accesslog="-",
    ).run()
    logger.debug(f"`http` server has been started on port {port}.")


@cli.command('https')
@click.option('--port',
              default=8443,
              show_default=True,
              help="HTTPS server port.")
@click.option('--scenario',
              required=True,
              type=click.Choice(HttpScenario.names()),
              help='HTTP server behaviour.')
def run_https_server(scenario, port):
    logger.debug("Starting `https` server...")
    app.config.update(
        SCENARIO=HttpScenario[scenario],
    )
    GunicornServer(
        app=app,
        bind=f"127.0.0.1:{port}",
        worker_class="gthread",
        threads=8,
        ssl=True,
        accesslog="-",
    ).run()
    logger.debug(f"`https` server has been started on port {port}.")
