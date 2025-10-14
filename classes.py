from validate import *


class User:
    def __init__(self, email, username, password):
        self.email = validate_email(email)
        self.username = validate_username(username)
        self.password = validate_password(password)


class Journey:
    def __init__(self, start, end, status="pending"):
        self.start = start
        self.end = end
        self.status = status

    def change_status(self, status):
        if status not in ("canceled", "done", "pending"):
            raise ChoiseError("only canceled , done, pending can be chosen")
        else:
            self.status = status


class Ticket:
    def __init__(self, journey: Journey, cost):
        self.journey = journey
        self.cost = cost


class Traveller(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)
        self.tickets = []

    def get_ticket(self, ticket: Ticket):
        if isinstance(ticket) == Ticket:
            self.tickets.append(ticket)
        else:
            raise TypeError("the type is not matched")

class Admin(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)