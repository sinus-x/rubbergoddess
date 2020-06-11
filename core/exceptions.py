class VerificationException(Exception):
    def __init__(self, message: str = None):
        self.message = message


class NotAnEmail(VerificationException):
    pass


class AlreadyInDatabase(VerificationException):
    pass


class EmailAlreadyInDatabase(AlreadyInDatabase):
    pass


class IDAlreadyInDatabase(AlreadyInDatabase):
    pass


class BadEmail(VerificationException):
    def __init__(self, message: str = None, expected: str = None):
        super().__init__(message)
        self.expected = expected
