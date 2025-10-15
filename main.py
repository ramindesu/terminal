from classes import *
from db import Database
from pprint import pprint
import os
from dotenv import load_dotenv,dotenv_values
os.system("clear")
load_dotenv()
dsn = os.getenv("DSN")

# dsn = 'dbname=terminal user=mohammadi password=shir884 host=localhost port=5432'


def admin_only(func):
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.current_user, Admin):
            raise NotAdmin(" Access denied: only admins can perform this action.")
        return func(self, *args, **kwargs)
    return wrapper


class Service:
    def __init__(self, title, options, data):
        self.title = title
        self.options = options
        self.data = data
        self.running = True
        self.current_user = None
        self.tickets = []
        self.dashboard = None  


    def create_tables(self):
        with Database(self.data) as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                wallet INT DEFAULT 0,
                registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS journey (
                id SERIAL PRIMARY KEY,
                start DATE,
                end_date DATE,
                origin VARCHAR(60),
                destination VARCHAR(60),
                status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending','done','canceled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS ticket (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                journey_id INT REFERENCES journey(id) ON DELETE CASCADE,
                price SMALLINT,
                registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                action VARCHAR(50),
                journey_id INT REFERENCES journey(id) ON DELETE CASCADE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        print(" Tables created successfully!")


    def add_log(self, action, journey_id=None):
        if not self.current_user:
            return
        with Database(self.data) as cur:
            cur.execute("""
                INSERT INTO logs (user_id, action, journey_id)
                VALUES (
                    (SELECT id FROM users WHERE email = %s LIMIT 1),
                    %s,
                    %s
                )
            """, (self.current_user.email, action, journey_id))


    def register_user(self):
        email = input("Enter email: ")
        username = input("Enter username: ")
        password = input("Enter password: ")
        user = Traveller(email, username, password)
        self.current_user = user
        self.dashboard = dashboard(user, 0)  

        with Database(self.data) as cur:
            cur.execute("""
                INSERT INTO users (username, email, wallet)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO NOTHING;
            """, (username, email, 0))

        self.add_log("register_user")
        print(f" User {user.username} registered successfully!")


    def register_admin(self):
        email = input("Enter admin email: ")
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        admin = Admin(email, username, password)
        self.current_user = admin

        with Database(self.data) as cur:
            cur.execute("""
                INSERT INTO users (username, email)
                VALUES (%s, %s)
                ON CONFLICT (email) DO NOTHING;
            """, (username, email))

        self.add_log("register_admin")
        print(f" Admin {admin.username} registered successfully!")


    @admin_only
    def add_ticket(self):
        start = input("Enter journey start date (YYYY-MM-DD): ")
        end = input("Enter journey end date (YYYY-MM-DD): ")
        origin = input("Enter origin: ")
        destination = input("Enter destination: ")
        cost = int(input("Enter ticket cost: "))

        with Database(self.data) as cur:

            cur.execute("""
                INSERT INTO journey (start, end_date, origin, destination)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (start, end, origin, destination))
            journey_id = cur.fetchone()[0]


            cur.execute("""
                INSERT INTO ticket (journey_id, price)
                VALUES (%s, %s);
            """, (journey_id, cost))

        journey = Journey(start, end)
        ticket = Ticket(journey, cost)
        self.tickets.append(ticket)
        self.add_log("add_ticket", journey_id)
        print(f" Ticket added for journey {start} => {end} (Cost: {cost}$)")


    def show_tickets(self):
        if not self.tickets:
            print(" No tickets available.")
            return
        print("\nAvailable tickets:")
        for i, ticket in enumerate(self.tickets, start=1):
            print(f"{i}. {ticket}")


    def buy_ticket(self):
        if not isinstance(self.current_user, Traveller):
            print(" Only travellers can buy tickets.")
            return

        if not self.tickets:
            print(" No tickets available for purchase.")
            return

        print("\nAvailable tickets to buy:")
        for i, ticket in enumerate(self.tickets, start=1):
            print(f"{i}. {ticket}")

        try:
            choice = int(input("Enter ticket number to buy: ")) - 1
            if choice < 0 or choice >= len(self.tickets):
                raise ChoiseError("Invalid choice")

            ticket = self.tickets[choice]

            if self.dashboard.wallet < ticket.cost:
                raise NotEnoughCash(f" Not enough money. You need {ticket.cost - self.dashboard.wallet}$ more.")

            self.dashboard._dashboard__wallet -= ticket.cost
            self.current_user.get_ticket(ticket)


            with Database(self.data) as cur:
                cur.execute("SELECT id FROM users WHERE email = %s;", (self.current_user.email,))
                user_id = cur.fetchone()[0]

                cur.execute("""
                    SELECT id FROM journey WHERE start = %s AND end_date = %s LIMIT 1;
                """, (ticket.journey.start, ticket.journey.end))
                journey_id = cur.fetchone()[0]

                cur.execute("""
                    UPDATE ticket
                    SET user_id = %s
                    WHERE journey_id = %s
                    LIMIT 1;
                """, (user_id, journey_id))

            self.add_log("buy_ticket", journey_id)
            print(f" Ticket purchased successfully! Remaining wallet: {self.dashboard.wallet}$")

        except (ValueError, ChoiseError, NotEnoughCash) as e:
            print(f" Error: {e}")


    def open_dashboard(self):
        if not isinstance(self.current_user, Traveller):
            print(" Only travellers have a dashboard.")
            return

        while True:
            print(f"\n Dashboard — {self.current_user.username}")
            print("1. Charge wallet")
            print("2. View history")
            print("3. Back to main menu")
            choice = input("Enter choice: ")

            if choice == "1":
                try:
                    amount = int(input("Enter amount to charge: "))
                    self.dashboard.charge_wallet(amount)
                    self.add_log("charge_wallet")
                except ValueError:
                    print(" Invalid amount.")
            elif choice == "2":
                print(f"\n Ticket history for {self.current_user.username}:")
                self.dashboard.history(self.current_user)
                self.add_log("view_history")
            elif choice == "3":
                break
            else:
                print("Invalid choice. Try again.")


    def show(self):
        print(f"\n==== {self.title} ====")
        for num, (desc, _) in self.options.items():
            print(f"{num}. {desc}")


    def run(self):
        while self.running:
            self.show()
            choice = input("Enter your choice: ")
            if choice in self.options:
                _, action = self.options[choice]
                try:
                    action()
                except Exception as e:
                    print(f" Error: {e}")
            else:
                print("Invalid choice. Try again.")



service = Service("Main Menu", {}, dsn)
service.options = {
    "1": ("Register User", service.register_user),
    "2": ("Register Admin", service.register_admin),
    "3": ("Add Ticket (Admin only)", service.add_ticket),
    "4": ("Show All Tickets", service.show_tickets),
    "5": ("Buy Ticket", service.buy_ticket),
    "6": ("Dashboard (Wallet & History)", service.open_dashboard),
    "7": ("Create Tables", service.create_tables),
    "8": ("Exit", lambda: setattr(service, "running", False))
}
service.run()