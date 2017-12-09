import asyncio
import logging

logger = logging.getLogger(__name__)


class TelnetServer:
    def __init__(self, host: str, port: int, protocol):
        self.loop = asyncio.get_event_loop()

        coro = self.loop.create_server(protocol, host, port)
        self.server = self.loop.run_until_complete(coro)

    def run(self):
        logger.debug(f"Serving on {self.server.sockets[0].getsockname()}")
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
