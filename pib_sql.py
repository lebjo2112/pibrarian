import sqlite3

class SQLib:
    def __init__(self):
        self.conn = sqlite3.connect('archives.db')
        self.c = self.conn.cursor()

    def get_table_data(self, table):
        self.c.execute('SELECT * FROM ' + table)
        data = self.c.fetchall()
        return data


psql = SQLib()
