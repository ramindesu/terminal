import psycopg
class Database:
    def __init__(self,dsn):
        """
        data = 'dbname=terminal user=postgres password=shir884 host=localhost '
        """
        self.dsn = dsn
        self.conn = ''
        self.cur = ''

    def __enter__(self):
        self.conn = psycopg.connect(self.dsn)
        self.cur = self.conn.cursor()
        return self.cur
    def __exit__(self,exc_type,exc_val,exc_tb):
        if exc_type == None:
            self.conn.commit()
        else:
            self.conn.rollback()
            print(f'error happened: {exc_val}')
        self.cur.close()        
        self.conn.close()
        
