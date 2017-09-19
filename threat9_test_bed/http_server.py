import logging
import os
import time

from flask import Flask, abort, redirect

http_server = Flask(__name__)
logger = logging.getLogger(__name__)

ALLOWED_METHODS = [
    "GET",
    "POST",
    "PATCH",
    "PUT",
    "OPTIONS",
    "DELETE",
]


@http_server.route('/', defaults={'path': ''}, methods=ALLOWED_METHODS)
@http_server.route('/<path:path>', methods=ALLOWED_METHODS)
def catch_all(path):
    scenario_handler = HTTP_SCENARIOS.get(http_server.config["SCENARIO"],
                                          error)
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
    time.sleep(60*60)


def error():
    abort(500)


HTTP_SCENARIOS = {
    "empty_response": empty_response,
    "trash": trash,
    "not_found": not_found,
    "found": found,
    "redirect": redirect_,
    "timeout": timeout,
    "error": error,
}
