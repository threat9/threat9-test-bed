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
