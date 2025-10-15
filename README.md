# Terminal Ticket Booking System

A terminal-based ticket and journey management system built with Python and PostgreSQL.  
Supports user registration, admin management, ticket purchasing, and a dashboard with wallet and ticket history.

---

## ⚡ Features

- Register regular users (Travellers) and Admins  
- Admins can add journeys and tickets  
- Display all available tickets  
- Travellers can purchase tickets and have them assigned in the database  
- User Dashboard:
  - Wallet management (charge wallet)
  - View ticket history
- Logging of all actions (user registration, admin actions, ticket purchases, wallet changes) in the database  
- Data is stored and managed in PostgreSQL  

---

## 🛠️ Requirements

- Python 3.9+  
- PostgreSQL  
- `psycopg` library for Python-PostgreSQL connectivity  

Install the library via pip:

```bash
pip install psycopg[binary]