import logging
import multiprocessing
import threading
from wsgiref.simple_server import make_server

from flask import Flask

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
