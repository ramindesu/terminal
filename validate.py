
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

class TypeError(Exception):
    ...

class ChoiseError(Exception):
    ...

username_validate = re.compile(r"^[a-zA-Z]{3,20}$")
password_validate = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z1-9]){8,}$"
)
email_validte = re.compile(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")

def validate_username(username):
    if not username_validate.match(username):
        raise ValidateError("must be letters and upper than 2 charachter")
    return username


def validate_password(password):
    if not password_validate.match(password):
        raise ValidateError("password is not valid")
    return password

def validate_email(email):
    if not email_validte.match(email):
        raise ValidateError("email is not okay")
    