import logging
import multiprocessing
import threading
import uuid
from wsgiref.simple_server import make_server

import requests
from flask import Flask, request

from ..http_service.gunicorn_server import GunicornServer
from .base_service import BaseService

logger = logging.getLogger(__name__)


class GunicornBasedHttpService(BaseService):
    """ `gunicorn` based HTTP service

    `Flask` application served using `gunicorn` in separate process using
    async workers (threads in this case).

    Application served by this base class suppose to handle unbuffered
    requests, `nginx` in this case is no option hence async workers.
    """
    def __init__(self, host: str, port: int, app: Flask, ssl=False):
        super().__init__(host, port)
        self.app = app
        self.server = GunicornServer(
            app=self.app,
            bind=f"{self.host}:{self.port}",
            worker_class="gthread",
            threads=8,
            ssl=ssl,
            accesslog="-",
        )
        self.server_process = multiprocessing.Process(target=self.server.run)

    def start(self):
        self.server_process.start()

    def teardown(self):
        self.server_process.terminate()
        self.server_process.join()


class WSGIRefBasedHttpService(BaseService):
    """ `wsgiref` based HTTP service

    `Flask` application served using `wsgiref` in separate thread.

    We can leverage shared state between main thread and thread handling
    `wsgiref` server and dynamically attach `Mock` object as view functions.
    """
    def __init__(self, host: str, port: int, app: Flask):
        super().__init__(host, port)
        self.app = app
        self.server = make_server(self.host, self.port, self.app)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.server_thread.start()

    def teardown(self):
        self.server.shutdown()
        self.server_thread.join()
        self.server.server_close()


class WerkzeugBasedHttpService(BaseService):
    """ `werkzeug` based HTTP service

    `Flask` application served using `werkzeug` in separate thread.

    We can leverage shared state between main thread and thread handling
    `wsgiref` server and dynamically attach `Mock` object as view functions.
    """
    def __init__(self, host: str, port: int, app: Flask, ssl=False):
        super().__init__(host, port)
        self.url_scheme = "https" if ssl else "http"
        self.terminate_url = uuid.uuid4().hex
        self.app = app

        self.app.add_url_rule(
            f"/{self.terminate_url}",
            "shutdown_server",
            self.shutdown_server,
            methods=['POST'],
        )

        self.server_thread = threading.Thread(
            target=self.app.run,
            args=(self.host, self.port),
            kwargs={"ssl_context": "adhoc"} if ssl else None
        )

    def start(self):
        self.server_thread.start()

    def teardown(self):
        requests.post(
            f"{self.url_scheme}://{self.host}:{self.port}"
            f"/{self.terminate_url}",
            verify=False,
        )
        self.server_thread.join()

    @staticmethod
    def shutdown_server():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Server terminated.", 200
