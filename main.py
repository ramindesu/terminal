from classes import *
from db import Database

dsn = 'dbname=terminal user=postgres password=shir884 host=localhost'

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


    def create_tables(self):
        with Database(self.data) as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
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
        self.add_log("register_user")
        print(f"User {user.username} registered successfully!")

    def register_admin(self):
        email = input("Enter admin email: ")
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        admin = Admin(email, username, password)
        self.current_user = admin
        self.add_log("register_admin")
        print(f" Admin {admin.username} registered successfully!")

    @admin_only
    def add_ticket(self):
        start = input("Enter journey start date (YYYY-MM-DD): ")
        end = input("Enter journey end date (YYYY-MM-DD): ")
        cost = int(input("Enter ticket cost: "))
        journey = Journey(start, end)
        ticket = Ticket(journey, cost)
        self.tickets.append(ticket)
        self.add_log("add_ticket")
        print(f"Ticket added for journey {start} → {end} (Cost: {cost})")

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


# Example usage
service = Service("Main Menu", {}, dsn)
service.options = {
    "1": ("Register User", service.register_user),
    "2": ("Register Admin", service.register_admin),
    "3": ("Add Ticket (Admin only)", service.add_ticket),
    "4": ("Create Tables", service.create_tables),
    "5": ("Exit", lambda: setattr(service, "running", False))
}
service.run()