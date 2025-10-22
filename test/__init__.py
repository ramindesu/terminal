import pytest
import psycopg
from classes import Traveller, Admin, Journey, Ticket
from main import Service

DSN = "dbname=terminal user=mohammadi password=shir884 host=localhost port=5432"


@pytest.fixture(scope="module")
def db_conn():
    """اتصال واقعی به دیتابیس"""
    conn = psycopg.connect(DSN)
    cur = conn.cursor()
    yield conn, cur
    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture
def clean_db(db_conn):

    conn, cur = db_conn
    cur.execute("""
        DROP TABLE IF EXISTS transactions, logs, ticket, journey, users CASCADE;
    """)
    conn.commit()


@pytest.fixture
def service_instance():
    return Service("Integration Test", {}, DSN)