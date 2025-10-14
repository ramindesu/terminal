from validate import *
class User:
    def __init__(self,email,username,password):
        self.email = validate_email(email)
        self.username = validate_username(username)
        self.password = validate_password(password)
class Ticket:
    pass

class Traveller(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)
        self.tickets = []

    def get_ticket(self,ticket:Ticket):
        if isinstance(ticket) == Ticket:
            self.tickets.append(ticket)
        else:
            raise TypeError("the type is not matched")
