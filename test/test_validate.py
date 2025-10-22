import pytest
from validate import *


def test_validate_username_valid():
    assert validate_username("Ramin") == "Ramin"
    assert validate_username("Ali") == "Ali"

def test_validate_username_invalid_short():
    with pytest.raises(ValidateError):
        validate_username("a")

def test_validate_username_invalid_with_numbers():
    with pytest.raises(ValidateError):
        validate_username("ramin123")

def test_validate_username_invalid_with_symbols():
    with pytest.raises(ValidateError):
        validate_username("ra_min")


def test_validate_password_valid():

    assert validate_password("Aa1@aaaa") == "Aa1@aaaa"
    assert validate_password("StrongP@ss1") == "StrongP@ss1"

def test_validate_password_invalid_no_uppercase():
    with pytest.raises(ValidateError):
        validate_password("weakpass1@")

def test_validate_password_invalid_no_digit():
    with pytest.raises(ValidateError):
        validate_password("NoNumber@")

def test_validate_password_invalid_no_symbol():
    with pytest.raises(ValidateError):
        validate_password("Password1")

def test_validate_password_invalid_too_short():
    with pytest.raises(ValidateError):
        validate_password("Aa1@a")


def test_validate_email_valid():
    assert validate_email("ramin@example.com") == "ramin@example.com"
    assert validate_email("user.test123@mail.co") == "user.test123@mail.co"

def test_validate_email_invalid_no_at():
    with pytest.raises(ValidateError):
        validate_email("raminexample.com")

def test_validate_email_invalid_no_domain():
    with pytest.raises(ValidateError):
        validate_email("ramin@")

def test_validate_email_invalid_bad_domain():
    with pytest.raises(ValidateError):
        validate_email("ramin@mail.")

def test_validate_email_invalid_special_chars():
    with pytest.raises(ValidateError):
        validate_email("ram in@mail.com")