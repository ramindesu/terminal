import re


class NotEnoughCash(Exception):

    pass

class JourneyStarted(Exception):

    pass

class ZeroValue(Exception):

    pass

class NotAdmin(Exception):

    pass

class ValidateError(Exception):

    pass

class InvalidType(Exception):

    pass

class ChoiceError(Exception):

    pass



username_validate = re.compile(r"^[a-zA-Z]{3,20}$")
password_validate = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$"
)
email_validate = re.compile(r"^[\w.\-]+@([\w\-]+\.)+[\w\-]{2,4}$")



def validate_username(username):

    if not username_validate.match(username):
        raise ValidateError("Username must contain only letters and be at least 3 characters long.")
    return username


def validate_password(password):

    if not password_validate.match(password):
        raise ValidateError(

        )
    return password


def validate_email(email):

    if not email_validate.match(email):
        raise ValidateError("Email format is invalid.")
    return email