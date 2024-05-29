"""
FIA Auth custom exceptions
"""


class UOWSError(Exception):
    """Problem authenticating with the user office web service"""


class ProposalAllocationsError(Exception):
    """Problem connecting with the proposal allocations api"""


class BadCredentialsError(Exception):
    """ "Bad Credentials Provided"""


class BadJWTError(Exception):
    """Raised when a bad jwt has been given to the service"""
