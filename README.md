<div align="center">

# 🎟️ Terminal Ticket Booking System  
### A Python + PostgreSQL CLI App for Managing Journeys & Tickets

🚀 *Simple · Powerful · Fully Database-Driven* 🚀  

</div>

---

## 🧩 Overview

This project simulates a **ticket booking system** built in Python, running entirely in the **terminal**,  
and powered by a **PostgreSQL database**.  

Admins can create journeys and tickets.  
Travellers can register, charge their wallet, reserve, buy, or cancel tickets — all through a clean CLI menu.

---

## ⚙️ Tech Stack

| Technology | Purpose |
|-------------|----------|
| 🐍 Python | Core application logic |
| 🗄️ PostgreSQL | Persistent data storage |
| 🔗 psycopg | Database connector |
| ⚙️ dotenv | Environment configuration |
| 🧾 pprint | Clean terminal output |

---

## 🚀 Features

| Category | Description |
|-----------|--------------|
| 👥 **User System** | Register as **Traveller** or **Admin** with validation |
| 🧭 **Admin Panel** | Create journeys, add tickets, and view total revenue |
| 💸 **Wallet System** | Users can charge wallet and track balance |
| 🎫 **Ticket System** | Reserve, buy, and cancel tickets with quantity tracking |
| 🔁 **Refunds** | Canceling returns 80% of the ticket price |
| 🧾 **Logging & Transactions** | Every action (buy, cancel, register, etc.) logged into PostgreSQL |
| 📊 **Dashboard** | Personal area for wallet & purchase history |

---

## 🗂️ Database Schema

| Table | Purpose |
|--------|----------|
| **users** | Stores user data, wallet, and registration date |
| **journey** | Contains start, end, origin, destination, and journey status |
| **ticket** | Connects journeys to users, tracks quantity, cost & status |
| **logs** | Keeps records of all performed actions |
| **transactions** | Tracks every buy, reserve, and cancel operation |

---

## 🛠️ Installation

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/ramindesu/terminal.git
cd terminal
```

### 2️⃣ Create a virtual environment  
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies  
```bash
pip install -r requirements.txt
```

### 4️⃣ Create your `.env` file in the root folder  
```env
DSN=dbname=terminal user=postgres password=yourpassword host=localhost port=5432
```

### 5️⃣ Run the program  
```bash
python main.py
```

---

## 💻 Example Usage

```bash
==== Main Menu ====
10. Create Tables
Tables created successfully!

1. Register Admin
Enter admin email: admin@example.com
Enter admin username: admin
Enter admin password: Admin123!
✅ Admin registered successfully!

3. Add Ticket (Admin only)
Enter journey start date: 2025-11-01
Enter journey end date: 2025-11-02
Enter origin: Tehran
Enter destination: Tabriz
Enter ticket cost: 100
Enter quantity: 3
🎫 Ticket added successfully!

1. Register User
Enter email: ramin@example.com
Enter username: ramin
Enter password: Ramin123!
✅ User registered successfully!

7. Dashboard → Charge wallet
💰 200$ added. New balance: 200$

5. Reserve Ticket
✅ Ticket reserved successfully (Qty: 2)

6. Confirm Reservation (Pay)
✅ Paid 100$ — Ticket status: paid | Wallet: 100$

7. Cancel Ticket
✅ Ticket canceled — Refund: 80$ | Wallet: 180$

8. Show Total Revenue (Admin)
💵 Total revenue: 100$
```

---

## 🔁 Ticket Lifecycle

| Action | Wallet Effect | Ticket Status | Quantity |
|---------|----------------|----------------|-----------|
| Reserve | No charge | `reserved` | −1 |
| Pay | −price | `paid` | −1 |
| Cancel | +80% refund | `canceled` | +1 |
| Sold Out | — | Journey status → `done` | 0 |

---

## 📜 Logs & Transactions

Every significant event is recorded in the database:

| Table | Example |
|--------|----------|
| **logs** | `"User ramin@example.com → buy_ticket"` |
| **transactions** | `('buy', 100)` , `('cancel', 80)` |

---

## 🧠 System Architecture

```text
User/Admin  ──▶  Service Layer (main.py)
                     │
                     ▼
               Business Logic
                     │
                     ▼
             PostgreSQL Database
```

---

## 🧑‍💻 Author

**Ramin Mohammadi**  
Backend Engineer  

🌐 **GitHub:** [@ramindesu](https://github.com/ramindesu)  
💼 **LinkedIn:** [ramin-desu](https://www.linkedin.com/in/ramin-desu-5428b6359/)

---

<div align="center">

Made with ❤️ using Python & PostgreSQL  
⭐ If you like this project, give it a **star** on GitHub!

</div>