from validate import *
from pprint import pprint


class User:
    def __init__(self, email, username, password):
        self.email = validate_email(email)
        self.username = validate_username(username)
        self.password = validate_password(password)


class Traveller(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)
        self.tickets = []

    def get_ticket(self, ticket):
        if isinstance(ticket, Ticket):
            self.tickets.append(ticket)
        else:
            raise TypeError("The type is not matched")


class Admin(User):
    def __init__(self, email, username, password):
        super().__init__(email, username, password)



class Journey:
    def __init__(self, start, end, origin=None, destination=None, status="pending"):
        self.start = start
        self.end = end
        self.origin = origin
        self.destination = destination
        self.status = status

    def change_status(self, status):
        if status not in ("canceled", "done", "pending"):
            raise ValueError("Only 'canceled', 'done', or 'pending' are allowed.")
        self.status = status

    def __str__(self):
        origin_dest = f"{self.origin} → {self.destination}" if self.origin and self.destination else ""
        return f"{self.start} => {self.end} | {origin_dest} | Status: {self.status}"


class Ticket:
    def __init__(self, journey: Journey, cost, quantity=1):
        self.journey = journey
        self.cost = cost
        self.quantity = quantity
        self.status = 'pending'

    def reserve(self):
        if self.status != 'pending':
            raise JourneyStarted("Ticket cannot be reserved now.")
        if self.quantity <= 0:
            raise ValueError("No tickets left.")
        self.quantity -= 1
        self.status = 'reserved'
        print(" Ticket reserved successfully.")

    def confirm(self):
        if self.status != 'reserved':
            raise JourneyStarted("Only reserved tickets can be confirmed.")
        self.status = 'paid'
        print(" Ticket payment confirmed.")

    def cancel_reservation(self):
        if self.status not in ('reserved', 'paid'):
            raise JourneyStarted("Only reserved or paid tickets can be canceled.")
        self.status = 'canceled'
        self.quantity += 1
        print(" Ticket canceled.")

    def __str__(self):
        return f"Journey: {self.journey} | Cost: {self.cost}$ | Status: {self.status} | Qty: {self.quantity}"



class dashboard:
    def __init__(self, user: Traveller, wallet=0):
        self.user = user
        self.__wallet = wallet

    @property
    def wallet(self):
        return self.__wallet

    def charge_wallet(self, amount):
        try:
            if amount <= 0:
                raise ZeroValue("Amount must be positive")
            self.__wallet += amount
            print(f" {amount}$ added. New balance: {self.__wallet}$")
        except ZeroValue as e:
            print(f" Error: {e}")

    def history(self):
        if not self.user.tickets:
            print("No tickets purchased yet.")
        else:
            print(" Ticket history:")
            for ticket in self.user.tickets:
                print(ticket)