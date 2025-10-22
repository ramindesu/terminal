from classes import *
from db import Database
import os
from dotenv import load_dotenv

os.system("clear")
load_dotenv()
dsn = os.getenv("DSN")

def admin_only(func):
    def wrapper(self, *args, **kwargs):
        if not isinstance(self.current_user, Admin):
            raise NotAdmin("Access denied: only admins can perform this action.")
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
                    quantity SMALLINT DEFAULT 1,
                    status VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending','reserved','paid','canceled')),
                    registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id) ON DELETE CASCADE,
                    action VARCHAR(50),
                    journey_id INT REFERENCES journey(id) ON DELETE CASCADE,
                    actor VARCHAR(60),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INT REFERENCES users(id) ON DELETE CASCADE,
                    ticket_id INT REFERENCES ticket(id) ON DELETE SET NULL,
                    type VARCHAR(20),
                    amount INT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        print("Tables created successfully!")

    def add_log(self, action, journey_id=None):

        if not self.current_user:
            return
        

        if isinstance(self.current_user, Admin):
            actor_type = "Admin"
        elif isinstance(self.current_user, Traveller):
            actor_type = "Traveller"
        else:
            actor_type = "Unknown"

        with Database(self.data) as cur:
            cur.execute("""
                INSERT INTO logs (user_id, action, journey_id, actor)
                VALUES (
                    (SELECT id FROM users WHERE email=%s LIMIT 1),
                    %s,
                    %s,
                    %s
                );
            """, (
                self.current_user.email,
                action,
                journey_id,
                actor_type
            ))

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
                VALUES (%s, %s, 0)
                ON CONFLICT (email) DO NOTHING;
            """, (username, email))
        print(f"User {username} registered successfully!")
        self.add_log("register_user")

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
        print(f"Admin {username} registered successfully!")
        self.add_log("register_admin")

    @admin_only
    def add_ticket(self):
        start = input("Enter journey start date (YYYY-MM-DD): ")
        end = input("Enter journey end date (YYYY-MM-DD): ")
        origin = input("Enter origin: ")
        destination = input("Enter destination: ")
        cost = int(input("Enter ticket cost: "))
        quantity = int(input("Enter ticket quantity: "))
        with Database(self.data) as cur:
            cur.execute("""
                INSERT INTO journey (start, end_date, origin, destination)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, (start, end, origin, destination))
            journey_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO ticket (journey_id, price, quantity)
                VALUES (%s, %s, %s);
            """, (journey_id, cost, quantity))
        ticket = Ticket(Journey(start, end, origin, destination), cost, quantity)
        self.tickets.append(ticket)
        print(f"Ticket added: {origin} → {destination} | {cost}$ | Qty: {quantity}")
        self.add_log("add_ticket", journey_id)

    def show_tickets(self):
        if not self.tickets:
            print("No tickets available.")
            return
        for i, t in enumerate(self.tickets, start=1):
            print(f"{i}. {t}")

    def buy_ticket_direct(self):
        if not isinstance(self.current_user, Traveller):
            print("Only travellers can buy tickets.")
            return
        if not self.tickets:
            print("No tickets available.")
            return
        for i, t in enumerate(self.tickets, start=1):
            print(f"{i}. {t}")
        choice = int(input("Select ticket number to buy directly: ")) - 1
        ticket = self.tickets[choice]
        if ticket.quantity <= 0:
            print("This ticket is sold out.")
            return
        if self.dashboard.wallet < ticket.cost:
            print("Not enough funds.")
            return
        ticket.status = "paid"
        ticket.quantity -= 1
        self.dashboard._dashboard__wallet -= ticket.cost
        self.current_user.get_ticket(ticket)
        with Database(self.data) as cur:
            cur.execute("SELECT id FROM users WHERE email=%s;", (self.current_user.email,))
            user_id = cur.fetchone()[0]
            cur.execute("""
                UPDATE ticket SET status='paid', quantity=%s, user_id=%s WHERE journey_id=(SELECT id FROM journey WHERE start=%s AND end_date=%s LIMIT 1);
            """, (ticket.quantity, user_id, ticket.journey.start, ticket.journey.end))
            cur.execute("""
                INSERT INTO transactions (user_id, ticket_id, type, amount)
                VALUES (%s, (SELECT id FROM ticket WHERE journey_id=(SELECT id FROM journey WHERE start=%s AND end_date=%s LIMIT 1)), 'buy', %s);
            """, (user_id, ticket.journey.start, ticket.journey.end, ticket.cost))
        print(f"Ticket purchased directly for {ticket.cost}$")
        self.add_log("buy_ticket_direct")

    def reserve_ticket(self):
        if not isinstance(self.current_user, Traveller):
            print("Only travellers can reserve tickets.")
            return
        if not self.tickets:
            print("No tickets available.")
            return
        for i, t in enumerate(self.tickets, start=1):
            print(f"{i}. {t}")
        choice = int(input("Enter ticket number to reserve: ")) - 1
        ticket = self.tickets[choice]
        ticket.reserve()
        self.current_user.get_ticket(ticket)
        with Database(self.data) as cur:
            cur.execute("SELECT id FROM users WHERE email=%s;", (self.current_user.email,))
            user_id = cur.fetchone()[0]
            cur.execute("""
                UPDATE ticket SET status='reserved', quantity=%s, user_id=%s WHERE journey_id=(SELECT id FROM journey WHERE start=%s AND end_date=%s LIMIT 1);
            """, (ticket.quantity, user_id, ticket.journey.start, ticket.journey.end))
            cur.execute("""
                INSERT INTO transactions (user_id, ticket_id, type, amount)
                VALUES (%s, (SELECT id FROM ticket WHERE journey_id=(SELECT id FROM journey WHERE start=%s AND end_date=%s LIMIT 1)), 'reserve', 0);
            """, (user_id, ticket.journey.start, ticket.journey.end))
        print("Ticket reserved successfully.")
        self.add_log("reserve_ticket")

    def confirm_reservation(self):
        if not isinstance(self.current_user, Traveller):
            print("Only travellers can confirm reservation.")
            return
        reserved = [t for t in self.current_user.tickets if t.status == "reserved"]
        if not reserved:
            print("No reserved tickets found.")
            return
        for i, t in enumerate(reserved, start=1):
            print(f"{i}. {t}")
        choice = int(input("Select reserved ticket to confirm: ")) - 1
        ticket = reserved[choice]
        if self.dashboard.wallet < ticket.cost:
            print("Not enough funds.")
            return
        ticket.status = "paid"
        ticket.quantity -= 1
        self.dashboard._dashboard__wallet -= ticket.cost
        with Database(self.data) as cur:
            cur.execute("SELECT id FROM users WHERE email=%s;", (self.current_user.email,))
            user_id = cur.fetchone()[0]
            cur.execute("""
                UPDATE ticket SET status='paid', quantity=%s WHERE user_id=%s;
            """, (ticket.quantity, user_id))
            cur.execute("""
                INSERT INTO transactions (user_id, ticket_id, type, amount)
                VALUES (%s, (SELECT id FROM ticket WHERE user_id=%s LIMIT 1), 'buy', %s);
            """, (user_id, user_id, ticket.cost))
        print(f"Reservation confirmed and paid {ticket.cost}$")
        self.add_log("confirm_reservation")

    def cancel_ticket(self):
        if not isinstance(self.current_user, Traveller):
            print("Only travellers can cancel tickets.")
            return
        if not self.current_user.tickets:
            print("No tickets to cancel.")
            return
        for i, t in enumerate(self.current_user.tickets, start=1):
            print(f"{i}. {t}")
        choice = int(input("Enter ticket number to cancel: ")) - 1
        ticket = self.current_user.tickets[choice]
        if ticket.status != "paid":
            print("Only paid tickets can be canceled.")
            return
        refund = int(ticket.cost * 0.8)
        self.dashboard._dashboard__wallet += refund
        ticket.status = "canceled"
        ticket.quantity += 1
        with Database(self.data) as cur:
            cur.execute("SELECT id FROM users WHERE email=%s;", (self.current_user.email,))
            user_id = cur.fetchone()[0]
            cur.execute("""
                UPDATE ticket SET status='canceled', quantity=%s WHERE user_id=%s;
            """, (ticket.quantity, user_id))
            cur.execute("""
                INSERT INTO transactions (user_id, ticket_id, type, amount)
                VALUES (%s, (SELECT id FROM ticket WHERE user_id=%s LIMIT 1), 'cancel', %s);
            """, (user_id, user_id, refund))
        print(f"Ticket canceled. Refund {refund}$ returned to wallet.")
        self.add_log("cancel_ticket")

    @admin_only
    def show_revenue(self):
        with Database(self.data) as cur:
            cur.execute("""
                SELECT 
                    COALESCE(SUM(CASE WHEN type='buy' THEN amount ELSE 0 END),0)+
                    COALESCE(SUM(CASE WHEN type='refund' THEN amount ELSE 0 END),0)
                FROM transactions;
            """)
            revenue = cur.fetchone()[0] or 0
        print(f"Total revenue (after refunds): {revenue}$")

    def open_dashboard(self):
        if not isinstance(self.current_user, Traveller):
            print("Only travellers have a dashboard.")
            return
        while True:
            print(f"\nDashboard — {self.current_user.username}")
            print("1. Charge wallet")
            print("2. View history")
            print("3. See wallet")
            print("4. Back")
            choice = input("Enter choice: ")
            if choice == "1":
                try:
                    amount = int(input("Enter amount: "))
                    self.dashboard.charge_wallet(amount)
                    self.add_log("charge_wallet")
                except ValueError:
                    print("Invalid amount.")
            elif choice == "2":
                self.dashboard.history()
            elif choice == "3":
                print(f"Wallet balance: {self.dashboard.wallet}$")
            elif choice == "4":
                break

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
                    print(f"Error: {e}")
            else:
                print("Invalid choice.")

service = Service("Main Menu", {}, dsn)
service.options = {
    "1": ("Register User", service.register_user),
    "2": ("Register Admin", service.register_admin),
    "3": ("Add Ticket (Admin only)", service.add_ticket),
    "4": ("Show Tickets", service.show_tickets),
    "5": ("Reserve Ticket", service.reserve_ticket),
    "6": ("Confirm Reservation (Pay)", service.confirm_reservation),
    "7": ("Buy Ticket Direct", service.buy_ticket_direct),
    "8": ("Cancel Ticket", service.cancel_ticket),
    "9": ("Dashboard", service.open_dashboard),
    "10": ("Show Revenue (Admin only)", service.show_revenue),
    "11": ("Create Tables", service.create_tables),
    "12": ("Exit", lambda: setattr(service, "running", False))
}
service.run()