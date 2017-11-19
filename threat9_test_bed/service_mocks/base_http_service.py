import logging
import multiprocessing
import socket
import threading
import time
from contextlib import closing
from wsgiref.simple_server import make_server

from flask import Flask

from ..gunicorn_server import GunicornServer

logger = logging.getLogger(__name__)


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return int(s.getsockname()[1])


class BaseHttpService:
    def __init__(self, host: str, port: int, app: Flask):
        self.host = host
        self.port = find_free_port() if port == 0 else port
        self.app = app

    def _wait_for_service(self):
        elapsed_time = 0
        start_time = time.time()
        while elapsed_time < 5:
            s = socket.socket()
            s.settimeout(1)
            try:
                s.connect((self.host, self.port))
            except (ConnectionRefusedError, ConnectionAbortedError):
                elapsed_time = time.time() - start_time
                s.close()
            else:
                s.close()
                break
        else:
            raise TimeoutError(f"{self.__class__.__name__} "
                               f"couldn't be set up before test.")

    def start(self):
        raise NotImplementedError()

    def teardown(self):
        raise NotImplementedError()

    def __enter__(self):
        logger.debug(f"Starting {self}...")
        self.start()
        self._wait_for_service()
        logger.debug(f"{self} has been started.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"Terminating {self}...")
        self.teardown()
        logger.debug(f"{self} has been terminated.")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(host='{self.host}', port={self.port})"
        )


class GunicornBasedHttpService(BaseHttpService):
    """ `gunicorn` based HTTP service

    `Flask` application served using `gunicorn` in separate process using
    async workers (threads in this case).

    Application served by this base class suppose to handle unbuffered
    requests, `nginx` in this case is no option hence async workers.
    """
    def __init__(self, host: str, port: int, app: Flask, ssl=False):
        super().__init__(host, port, app)
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


class WSGIRefBasedHttpService(BaseHttpService):
    """ `wsgiref` based HTTP service

    `Flask` application served using `wsgiref` in separate thread.

    We can leverage shared state between main thread and thread handling
    `wsgiref` server and dynamically attach `Mock` object as view functions.
    """
    def __init__(self, host: str, port: int, app: Flask):
        super().__init__(host, port, app)
        self.server = make_server(self.host, self.port, self.app)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def start(self):
        self.server_thread.start()

    def teardown(self):
        self.server.shutdown()
        self.server_thread.join()
        self.server.server_close()
