import sqlite3


class db_help:
    def __init__(self, db_name):
        """Method to initialize database class and check it
        - db_name - path to our database"""
        self.db_name = db_name

        self.connect()
        self.close()

    def connect(self):
        """Method to initialize connection with database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print('Connect successes')
        except Exception as e:
            print(e)

    def close(self):
        """Method to close connection with database"""
        if self.conn:
            self.conn.close()

    def add_info(self, table, column, info):
        """Method to add info into our table
        - table - name of table in with we want to paste our info
        - column - list of name of column(s) in with we want to paste the info
        * if you want to pate in all columns
        - info - list of information what we want to paste
        """
        self.connect()
        a = "'" + "', '".join(info) + "'"
        column_formatted = ', '.join(column)
        print("INSERT OR IGNORE INTO {table} ({column}) VALUES ({quest})".format(table=table, column=column_formatted,
                                                                                 quest=a))
        self.cursor.execute(
            "INSERT OR IGNORE INTO {table} ({column}) VALUES ({quest})".format(table=table, column=column_formatted,
                                                                               quest=a))

        self.conn.commit()
        self.close()

    def return_info(self, where, what='*'):
        """This method is return info
        - where - name of table where info is exists
        - what - name(s) of column(s) where info is settle down"""
        self.connect()
        return_inf = self.cursor.execute("SELECT {what} FROM {where}".format(what=what, where=where)).fetchall()
        self.close()
        return return_inf

    def have_db(self):
        """This method is returning names of all tables in database"""
        self.connect()
        names = list(zip(*self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and "
                                              "name NOT LIKE 'sqlite_%'")))[0]
        return names

    def make_db(self, name):
        """Method to create new database (for difference queue)
        - name - name of new database"""
        self.connect()
        if name not in self.have_db(name):
            self.cursor.execute("CREATE TABLE '{}' ("
                                "number INTEGER PRIMARY KEY AUTOINCREMENT,"
                                " name   STRING  UNIQUE)".format(name))
        else:
            print('We already have the same table')
        self.close()

    def del_db(self, name):
        """Method to delete database
        - name - name of database we want to delete"""
        self.connect()
        if name in self.have_db(name):
            self.cursor.execute("DROP TABLE '{}'".format(name))
            print('{} has deleted'.format(name))
        else:
            print('We haven`t the same table')
        self.close()

    def del_row(self, table, name, column='name'):
        """Method to delete row in database and move queue
         - table - name of table in with we want to paste our info
        - name - name what we want to delete
        - column - name of column where name is settle down
        """
        self.connect()
        if list(self.cursor.execute("SELECT number "
                                    " FROM {table} WHERE {row}='{name}'".format(table=table, name=name,
                                                                                row=column))):
            a = list(self.cursor.execute("SELECT number "
                                         " FROM {table} WHERE {row}='{name}'".format(table=table, name=name, row=column)))[
                0][0]
            print(a)
            self.cursor.execute("DELETE FROM {table}"
                                " WHERE {row}='{name}'".format(row=column, table=table, name=name))
            self.cursor.execute("UPDATE {table}"
                                " SET number=number-1"
                                " WHERE number>{a}".format(table=table, row=column, name=name, a=a))

        self.conn.commit()
        self.close()
