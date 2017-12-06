import tempfile
from pathlib import Path

from gunicorn.app.base import BaseApplication
from OpenSSL import crypto
from werkzeug.serving import generate_adhoc_ssl_pair


class GunicornServer(BaseApplication):
    def __init__(self, app, **kwargs):
        self.options = kwargs
        self.application = app
        super().__init__()

    def load_config(self):
        if self.options.get("ssl"):
            cert_path, pkey_path = self.generate_devel_ssl_pair()
            self.options["certfile"] = str(cert_path)
            self.options["keyfile"] = str(pkey_path)

        config = {
            key: value for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

    @staticmethod
    def generate_devel_ssl_pair() -> (Path, Path):
        cert_path = Path(tempfile.gettempdir()) / "threat9-test-bed.crt"
        pkey_path = Path(tempfile.gettempdir()) / "threat9-test-bed.key"

        if not cert_path.exists() or not pkey_path.exists():
            cert, pkey = generate_adhoc_ssl_pair()
            with open(cert_path, "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            with open(pkey_path, "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))

        return cert_path, pkey_path
