import logging
import os
import time

from flask import Flask, abort, redirect

from .scenarios import HttpScenario

logger = logging.getLogger(__name__)

app = Flask(__name__)

ALLOWED_METHODS = [
    "GET",
    "POST",
    "PATCH",
    "PUT",
    "OPTIONS",
    "DELETE",
]


@app.route('/', defaults={'path': ''}, methods=ALLOWED_METHODS)
@app.route('/<path:path>', methods=ALLOWED_METHODS)
def catch_all(path):
    scenario_handler = SCENARIO_TO_HANDLER_MAP.get(
        app.config["SCENARIO"],
        error,
    )
    logger.debug(
        f"Executing '{scenario_handler.__name__}' scenario handler..."
    )
    return scenario_handler()


def empty_response():
    return "", 200


def trash():
    return os.urandom(100), 200


def not_found():
    abort(404)


def found():
    return "OK", 200


def redirect_():
    return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


def timeout():
    time.sleep(60 * 60)


def error():
    abort(500)


SCENARIO_TO_HANDLER_MAP = {
    HttpScenario.EMPTY_RESPONSE: empty_response,
    HttpScenario.TRASH: trash,
    HttpScenario.NOT_FOUND: not_found,
    HttpScenario.FOUND: found,
    HttpScenario.REDIRECT: redirect_,
    HttpScenario.TIMEOUT: timeout,
    HttpScenario.ERROR: error,
}
