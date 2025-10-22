import pytest
from datetime import date
from validate import (
    ValidateError,
    JourneyStarted,
    ZeroValue,
)
from classes import (
    User,
    Traveller,
    Admin,
    Journey,
    Ticket,
    dashboard,
)


def test_user_valid_data():
    user = User("ramin@example.com", "Ramin", "Aa1@abcd")
    assert user.email == "ramin@example.com"
    assert user.username == "Ramin"
    assert user.password == "Aa1@abcd"


def test_user_invalid_email():
    with pytest.raises(ValidateError):
        User("ramin@", "Ramin", "Aa1@abcd")


def test_user_invalid_username():
    with pytest.raises(ValidateError):
        User("ramin@example.com", "ra", "Aa1@abcd")


def test_user_invalid_password():
    with pytest.raises(ValidateError):
        User("ramin@example.com", "Ramin", "weakpass")


def test_traveller_inherits_user_and_get_ticket():
    t = Traveller("trav@example.com", "Trav", "Aa1@abcd")
    j = Journey("2025-10-20", "2025-10-21", "Tehran", "Paris")
    ticket = Ticket(j, 100)
    t.get_ticket(ticket)
    assert len(t.tickets) == 1
    assert isinstance(t.tickets[0], Ticket)


def test_traveller_get_ticket_invalid_type():
    t = Traveller("trav@example.com", "Trav", "Aa1@abcd")
    with pytest.raises(TypeError):
        t.get_ticket("not_ticket")


def test_admin_inherits_user():
    a = Admin("admin@example.com", "AdminUser", "Aa1@abcd")
    assert isinstance(a, User)
    assert a.email == "admin@example.com"



def test_journey_str_and_status_change():
    j = Journey("2025-10-20", "2025-10-21", "Tehran", "Berlin")
    assert "Tehran" in str(j)
    j.change_status("done")
    assert j.status == "done"


def test_journey_invalid_status():
    j = Journey("2025-10-20", "2025-10-21")
    with pytest.raises(ValueError):
        j.change_status("flying")



def test_ticket_reserve_confirm_cancel(capsys):
    j = Journey("2025-10-20", "2025-10-21")
    t = Ticket(j, 200, quantity=2)
    t.reserve()
    out = capsys.readouterr().out
    assert "reserved" in t.status
    assert "Ticket reserved successfully" in out

    t.confirm()
    assert t.status == "paid"

    t.cancel_reservation()
    assert t.status == "canceled"
    assert t.quantity == 2


def test_ticket_reserve_with_zero_quantity():
    j = Journey("2025-10-20", "2025-10-21")
    t = Ticket(j, 100, quantity=0)
    with pytest.raises(ValueError):
        t.reserve()


def test_ticket_invalid_confirm_order():
    j = Journey("2025-10-20", "2025-10-21")
    t = Ticket(j, 100)
    with pytest.raises(JourneyStarted):
        t.confirm()


def test_ticket_invalid_cancel_order():
    j = Journey("2025-10-20", "2025-10-21")
    t = Ticket(j, 100)
    with pytest.raises(JourneyStarted):
        t.cancel_reservation()



def test_dashboard_charge_wallet_valid(capsys):
    t = Traveller("trav@example.com", "Trav", "Aa1@abcd")
    dash = dashboard(t)
    dash.charge_wallet(100)
    output = capsys.readouterr().out
    assert "100$ added" in output
    assert dash.wallet == 100


def test_dashboard_charge_wallet_invalid(capsys):
    t = Traveller("trav@example.com", "Trav", "Aa1@abcd")
    dash = dashboard(t)
    dash.charge_wallet(-50)
    output = capsys.readouterr().out
    assert "Error" in output


def test_dashboard_history(capsys):
    t = Traveller("trav@example.com", "Trav", "Aa1@abcd")
    dash = dashboard(t)
    dash.history()
    output = capsys.readouterr().out
    assert "No tickets" in output

    j = Journey("2025-10-20", "2025-10-21", "Tehran", "Paris")
    ticket = Ticket(j, 100)
    t.get_ticket(ticket)
    dash.history()
    output = capsys.readouterr().out
    assert "Tehran" in output