'''
Please note:

The first file that you should run in this level is tests.py for database creation, with all tests passing.
Remember that running the hack.py will change the state of the database, causing some tests inside tests.py
to fail.

If you like to return to the initial state of the database, please delete the database (level-4.db) and run 
the tests.py again to recreate it.
'''

import sqlite3
import re
from contextlib import closing
import os
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def source():
    return DB_CRUD_ops().get_stock_info(request.args["input"])


class Connect(object):

    # helper function creating database with the connection
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
        except sqlite3.Error as e:
            print(f"ERROR: {e}")
        return connection

class Create(object):

    def __init__(self):
        con = Connect()
        try:
            # creates a dummy database inside the folder of this challenge
            path = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(path, 'level-4.db')
            db_con = con.create_connection(db_path)
            cur = db_con.cursor()

            # checks if tables already exist, which will happen when re-running code
            table_fetch = cur.execute(
                '''
                SELECT name 
                FROM sqlite_master 
                WHERE type='table'AND name='stocks';
                ''').fetchall()

            # if tables do not exist, create them and insert dummy data
            if table_fetch == []:
                cur.execute(
                    '''
                    CREATE TABLE stocks
                    (date text, symbol text, price real)
                    ''')

                # inserts dummy data to the 'stocks' table, representing average price on date
                cur.execute(
                    "INSERT INTO stocks VALUES ('2022-01-06', 'MSFT', 300.00)")
                db_con.commit()

        except sqlite3.Error as e:
            print(f"ERROR: {e}")

        finally:
            db_con.close()

class DB_CRUD_ops:

    def _connect(self):
        Create()
        return sqlite3.connect(os.path.join(os.path.dirname(__file__), 'level-4.db'))

    def _execute(self, statement, parameters):
        with closing(self._connect()) as connection, connection:
            return connection.execute(statement, parameters).fetchall()

    def get_stock_info(self, stock_symbol):
        output = "[METHOD EXECUTED] get_stock_info\n[QUERY] "
        output += f"SELECT * FROM stocks WHERE symbol = '{stock_symbol}'\n"
        if any(char in stock_symbol for char in "';%&^!#-"):
            return output + "CONFIRM THAT THE ABOVE QUERY IS NOT MALICIOUS TO EXECUTE"
        rows = self._execute("SELECT * FROM stocks WHERE symbol = ?", (stock_symbol,))
        return output + "".join(f"[RESULT] {row}" for row in rows)

    def get_stock_price(self, stock_symbol):
        output = "[METHOD EXECUTED] get_stock_price\n[QUERY] "
        output += f"SELECT price FROM stocks WHERE symbol = '{stock_symbol}'\n"
        rows = self._execute("SELECT price FROM stocks WHERE symbol = ?", (stock_symbol,))
        return output + "".join(f"[RESULT] {row}\n" for row in rows)

    def update_stock_price(self, stock_symbol, price):
        if not isinstance(price, float):
            raise ValueError("ERROR: stock price provided is not a float")
        self._execute("UPDATE stocks SET price = ? WHERE symbol = ?", (price, stock_symbol))
        return (
            "[METHOD EXECUTED] update_stock_price\n[QUERY] "
            f"UPDATE stocks SET price = '{price:g}' WHERE symbol = '{stock_symbol}'\n"
        )

    # The reporting interface accepts stock lookups only.
    def _report_rows(self, query):
        match = re.fullmatch(
            r"\s*SELECT\s+(price|\*)\s+FROM\s+stocks\s+WHERE\s+symbol\s*=\s*'([A-Za-z0-9.\-]+)'\s*",
            query,
            re.IGNORECASE,
        )
        if match is None:
            raise ValueError("Only stock lookup queries are supported")
        column, symbol = match.groups()
        if column.lower() == "price":
            return self._execute("SELECT price FROM stocks WHERE symbol = ?", (symbol,))
        return self._execute("SELECT * FROM stocks WHERE symbol = ?", (symbol,))

    def exec_multi_query(self, query):
        output = "[METHOD EXECUTED] exec_multi_query\n"
        for lookup in filter(str.strip, query.split(';')):
            output += f"[QUERY]{lookup}\n"
            output += "".join(f"[RESULT] {row} " for row in self._report_rows(lookup))
        return output

    def exec_user_script(self, query):
        rows = self._report_rows(query)
        output = f"[METHOD EXECUTED] exec_user_script\n[QUERY] {query}\n"
        return output + "".join(f"[RESULT] {row}" for row in rows)
