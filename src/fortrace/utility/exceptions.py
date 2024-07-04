"""Specific exceptions.

"""


class NetworkError(Exception):
    """Error with some network component or the virsh command."""
    pass


class ForTraceException(Exception):
    """Generic ForTrace specific exception, to help differentiate from other exceptions.
    All other custom exceptions have to inherit this class."""

    def __init__(self, *args):
        Exception.__init__(self, *args)


class DomainException(ForTraceException):
    """To be thrown when something cannot be done with a domain"""


class SetupException(ForTraceException):
    """To be thrown if something unexpected happens during a setup process"""


class ConfigurationError(ForTraceException):
    """Configuration-specific exception"""


class MultiStageAttackException(ForTraceException):
    """Multi-stage attack exception, thrown when something is not working during an attack"""


class ServerInteractionException(ForTraceException):
    """Server interaction exception, thrown when interaction with server encounters an issue"""
