import logging
import socket
import time
from contextlib import closing

logger = logging.getLogger(__name__)


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return int(s.getsockname()[1])


class BaseService:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = find_free_port() if port == 0 else port

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
