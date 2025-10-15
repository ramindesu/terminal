from validate import *
from pprint import pprint

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
            raise ValueError("Only 'canceled', 'done', or 'pending' are allowed.")
        self.status = status

    def __str__(self):
        return f"{self.start} => {self.end} | Status: {self.status}"


class Ticket:
    def __init__(self, journey: Journey, cost):
        self.journey = journey
        self.cost = cost

    def __str__(self):
        return f"Journey: {self.journey} | Cost: {self.cost}$"


class Traveller(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)
        self.tickets = []

    def get_ticket(self, ticket: Ticket):
        if isinstance(ticket, Ticket):
            self.tickets.append(ticket)
        else:
            raise TypeError("The type is not matched")


class Admin(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)

class dashboard():
    def __init__(self,user:Traveller,wallet):
        self.user = user
        self.__wallet = wallet

    @property 
    def wallet(self):
        return self.__wallet
    
    def charge_wallet(self,amount):
        try:
            if amount < 0:
                raise ZeroValue("cant be smaller than 0 sir")
            self.__wallet+=amount
            print(f"the amount:{amount}$ just added to ur wallet new balance: {self.__wallet} ")
        except ZeroValue as e:
            print(f'error: {e}')
        
    def history(self,user:Traveller):
        for trip in user.tickets:
            pprint(trip)
    