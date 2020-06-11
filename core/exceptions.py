class RubbergoddessException(Exception):
    def __init__(self, message: str = None):
        self.message = message


class VerificationException(RubbergoddessException):
    pass


class NotInDatabase(VerificationException):
    pass


class NotAnEmail(VerificationException):
    pass


class AlreadyInDatabase(VerificationException):
    pass


class EmailAlreadyInDatabase(AlreadyInDatabase):
    pass


class IDAlreadyInDatabase(AlreadyInDatabase):
    pass


class BadEmail(VerificationException):
    def __init__(self, message: str = None, constraint: str = None):
        super().__init__(message)
        self.constraint = constraint


class ProblematicVerification(VerificationException):
    def __init__(self, status: str, message: str = None):
        super().__init__(message)
        self.status = status
