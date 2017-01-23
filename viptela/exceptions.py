class Error(Exception):
    """Base class for other exceptions"""
    pass


class LoginTimeoutError(Error):
    """Raised login to device times out"""
    pass


class LoginCredentialsError(Error):
    """Raised when there is a problem with the user credentials"""
    pass
