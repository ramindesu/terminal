from db import Database
from os import system
system("clear")


dsn = 'dbname=terminal user=postgres password=shir884 host=localhost'

class Service:
    def __init__(self, title, options, data):
        self.title = title
        self.options = options
        self.data = data
        self.running = True

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
            CREATE TABLE IF NOT EXISTS ticket (
                id SERIAL PRIMARY KEY,
                price SMALLINT,
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
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                action VARCHAR(50),
                journey_id INT REFERENCES journey(id) ON DELETE CASCADE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        print("Tables created successfully ✅")

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
                action()
            else:
                print("Invalid choice. Try again.")



service = Service("Main Menu", {}, dsn)
service.options = {
    "1": ("Create Tables", service.create_tables),
    "2": ("Exit", lambda: setattr(service, "running", False))
}
service.run()