import sqlite3


def connect_close(func):
    """Decorator to do connect to database, and close connection"""

    def wrap(*args, **kwargs):
        args[0].connect()
        a = func(*args, **kwargs)
        args[0].conn.commit()
        args[0].close()
        return a

    return wrap


def connect_dec(func):
    """Decorator to do connect to database"""

    def wrap(*args, **kwargs):
        args[0].connect()
        a = func(*args, **kwargs)
        return a

    return wrap


class db_help:
    def __init__(self, db_name):
        """Method to initialize database class and check it
        - db_name - path to our database"""
        self.db_name = db_name

        self.connect()
        self.close()
        self.unzip = lambda a: list(zip(*a))[0] if list(zip(*a)) else list(zip(*a))

    def connect(self):
        """Method to initialize connection with database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    def close(self):
        """Method to close connection with database"""
        if self.conn:
            self.conn.close()

    @connect_close
    def add_info(self, table, column, info):
        """Method to add info into our table
        - table - name of table in with we want to paste our info
        - column - list of name of column(s) in with we want to paste the info
        * if you want to paste in all columns
        - info - list of information what we want to paste
        """
        if isinstance(info, str):
            info_form = info
        else:
            info_form = info[0]
        if info_form not in self.unzip(self.return_info(table, column)):
            if column == '*':
                column_formatted = ""
                a = "'" + "', '".join(info) + "'"

            elif isinstance(column, str):
                column_formatted = f'({column})'
                a = "'" + info + "'"
            else:
                column_formatted = '(' + ', '.join(column) + ')'
                a = "'" + "', '".join(info) + "'"
            print(column_formatted)
            self.cursor.execute(
                "INSERT OR IGNORE INTO {table} {column} VALUES ({quest})".format(table=table, column=column_formatted,
                                                                                 quest=a))

            return True
        else:
            print(self.unzip(self.return_info(table, column)))
            print('We already had this info')
            return False

    def add_name_id(self, id, name):
        """Method to make your adding id and name to the table 'user' easier"""
        return self.add_info('users', '*', [id, name])

    @connect_dec
    def return_info(self, where, what='*'):
        """This method is return info
        - where - name of table where info is exists
        - what - name(s) of column(s) where info is settle down"""
        if not isinstance(what, str):
            what = ', '.join(what)

        return_inf = self.cursor.execute("SELECT {what} FROM {where}".format(what=what, where=where)).fetchall()
        return return_inf

    @connect_dec
    def have_db(self):
        """This method is returning names of all tables in database"""
        names = list(zip(*self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and "
                                              "name NOT LIKE 'sqlite_%'")))[0]
        return names

    @connect_close
    def make_db(self, name):
        """Method to create new database (for difference queue)
        - name - name of new database"""
        if name not in self.have_db():
            self.cursor.execute("CREATE TABLE '{}' ("
                                "number INTEGER PRIMARY KEY AUTOINCREMENT,"
                                " name   STRING  UNIQUE)".format(name))
            return True
        else:
            print('We already have the same table')
            return False

    @connect_close
    def del_db(self, name):
        """Method to delete database
        - name - name of database we want to delete"""
        if name in self.have_db():
            self.cursor.execute("DROP TABLE '{}'".format(name))
            print('{} has deleted'.format(name))
            return True
        else:
            print('We haven`t the same table')
            return False

    @connect_dec
    def return_names(self, where):
        """This method is return list of names from table with id
        - where - name of table where info is exists"""
        return_inf = self.cursor.execute(
            "Select u.name FROM {where} w JOIN users u ON w.name=u.id".format(where=where)).fetchall()
        return self.unzip(return_inf)

    @connect_close
    def update_name(self, person_id, name):
        """This method is to update persons name
        - id - persons id number
        - name - name in what we want to change"""
        if self.cursor.execute('SELECT name FROM users WHERE id={id}'.format(id=person_id)):
            self.cursor.execute('UPDATE users'
                                f" SET name = '{name}'"
                                f" WHERE id = '{person_id}'")
        else:
            self.add_info('users', ['id', 'name'], [person_id, name])

    @connect_close
    def return_name(self, person_id):
        """This method is returning persons name
        - id - persons id number"""
        if self.cursor.execute('SELECT name FROM users WHERE id={id}'.format(id=person_id)).fetchall():
            a = self.cursor.execute('SELECT name FROM users WHERE id={id}'.format(id=person_id)).fetchall()
            return self.unzip(a)[0]
        else:
            print('We haven`t your name in our database, please enter it')
            return False

    @connect_close
    def delete_info(self, table, column, info):
        """Method to delete info from our table
               - table - name of table from  we want to delete our info
               - column - list of name of column(s) from we want to delete the info
               * if you want to delete from all records
               - info - list of information what we want to delete
               """
        a = "'" + "', '".join(info) + "'"
        column_formatted = ', '.join(column)
        print("DELETE FROM {table} WHERE {column} = {quest}".format(table=table, column=column_formatted,
                                                                    quest=a))
        self.cursor.execute(
            "DELETE FROM {table} WHERE {column} = {quest}".format(table=table, column=column_formatted,
                                                                  quest=a))

    @connect_close
    def del_row(self, table, name, column='name'):
        """Method to delete row in database and move queue
         - table - name of table in with we want to paste our info
        - name - name what we want to delete
        - column - name of column where name is settle down
        """
        if list(self.cursor.execute("SELECT number "
                                    " FROM {table} WHERE {row}='{name}'".format(table=table, name=name,
                                                                                row=column))):
            a = list(self.cursor.execute("SELECT number "
                                         " FROM {table} WHERE {row}='{name}'".format(table=table, name=name,
                                                                                     row=column)))[0][0]
            print(a)
            self.cursor.execute("DELETE FROM {table}"
                                " WHERE {row}='{name}'".format(row=column, table=table, name=name))
            self.cursor.execute("UPDATE {table}"
                                " SET number=number-1"
                                " WHERE number>{a}".format(table=table, row=column, name=name, a=a))
            return True
        return False
