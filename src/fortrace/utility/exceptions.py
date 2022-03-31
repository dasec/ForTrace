"""Specific exceptions.

"""

class NetworkError(Exception):
    """Error with some network component or the virsh command."""
    pass

class NotImplemented(Exception):
    """The used function is actually not implemented!"""
    pass
