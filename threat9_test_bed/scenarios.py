from enum import Enum, unique


@unique
class HttpScenario(Enum):
    EMPTY_RESPONSE = "empty_response"
    TRASH = "trash"
    NOT_FOUND = "not_found"
    FOUND = "found"
    REDIRECT = "redirect"
    TIMEOUT = "timeout"
    ERROR = "error"

    @staticmethod
    def names():
        return [element.name for element in HttpScenario]


@unique
class TelnetScenario(Enum):
    GENERIC = "generic"
    AUTHORIZED = "authorized"
    NOT_AUTHORIZED = "not_authorized"
    TIMEOUT = "timeout"

    @staticmethod
    def names():
        return [element.name for element in TelnetScenario]
