import discord


class RubbergoddessException(Exception):
    def __init__(self, message: str = None):
        self.message = message


##
## Gatekeeper
##
# fmt: off
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
class SubmitWithoutCode(VerificationException):
    pass
class ProblematicVerification(VerificationException):
    def __init__(self, status: str):
        super().__init__()
        self.status = status
class WrongVerificationCode(VerificationException):
    def __init__(self, member: discord.Member, their: str, database: str):
        super().__init__()
        self.member = member
        self.their = their
        self.database = database
# fmt: on

##
## Shop
##
# fmt: off
class ShopException(RubbergoddessException):
    pass
class ForbiddenNicknameCharacter(ShopException):
    def __init__(self, forbidden: str):
        super().__init__()
        self.forbidden = forbidden
# fmt: on
