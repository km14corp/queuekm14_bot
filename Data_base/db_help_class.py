import sqlite3


# SELECT (number+1) from bookings where event_id=1 ORDER by number desc LIMIT 1; to get new next available number in the queue
def connect_close_decorator(func):
    """Decorator to do connect to database, and close connection"""

    def wrap(*args, **kwargs):
        args[0].connect()
        a = func(*args, **kwargs)
        args[0].conn.commit()
        args[0].close()
        return a

    return wrap


def connect_decorator(func):
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
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        """Method to close connection with database"""
        if self.conn:
            self.conn.close()

    @connect_close_decorator
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
        if info_form not in self.unzip(self.get_info(table, column)):
            self.connect()
            if column == '*':
                column_formatted = ""
                a = "'" + "', '".join(info) + "'"

            elif isinstance(column, str):
                column_formatted = f'({column})'
                a = "'" + info + "'"
            else:
                column_formatted = '(' + ', '.join(column) + ')'
                a = "'" + "', '".join(info) + "'"
            self.cursor.execute(
                f"INSERT OR IGNORE INTO '{table}' {column_formatted} VALUES ({a})")

            return True
        else:
            print('We already had this info')
            return False

    def add_user(self, user_id, name):
        """Method to make your adding id and name to the table 'user' easier"""
        return self.add_info('users', '*', [user_id, name])

    @connect_close_decorator
    def get_info(self, table, what='*', where='1=1'):
        """This method is return info
        - where - name of table where info is exists
        - what - name(s) of column(s) where info is settle down"""
        if not isinstance(what, str):
            what = ', '.join(what)
        return_inf = self.cursor.execute(
            f"SELECT {what} FROM '{table}' WHERE {where}").fetchall()
        return return_inf

    def get_courses(self, what='*'):
        result = self.get_info('courses', what)
        self.connect()
        if (len(what) > 1 and type(what) == tuple) or what == '*':
            return result
        else:
            return self.unzip(result)

    @connect_close_decorator
    def get_event_id(self, name):
        result = self.cursor.execute(f"SELECT id FROM events WHERE name='{name}'").fetchall()
        return result[0][0]

    @connect_close_decorator
    def get_course_id(self, course_name):
        result = self.cursor.execute(f"SELECT id FROM courses WHERE name='{course_name}'").fetchall()
        return result[0][0]

    @connect_close_decorator
    def get_queue_number(self, event_id):
        result = self.cursor.execute(f"SELECT Count(number) from bookings WHERE event_id= {event_id}").fetchall()
        return result[0][0] + 1

    @connect_close_decorator
    def is_booked(self, user_id, event_id):
        if self.cursor.execute(f"SELECT * from bookings WHERE event_id= {event_id} and user_id = {user_id}").fetchall():
            return True
        else:
            return False

    def get_events(self):
        result = self.get_info('events', 'name')
        self.connect()
        return list(self.unzip(result))

    def book_user(self, user_id, event_id):
        queue_number = self.get_queue_number(event_id)
        self.connect()
        self.add_info('bookings', ['event_id', 'user_id', 'number'],
                      [str(event_id), str(user_id), str(queue_number)])

    @connect_close_decorator
    def unbook_user(self, user_id, event_id):
        self.cursor.execute(f"DELETE FROM bookings WHERE user_id={user_id} and event_id={event_id}")

    @connect_close_decorator
    def update_user_name(self, user_id, name):
        """This method is to update persons name
        - id - persons id number
        - name - name in what we want to change"""
        if self.cursor.execute('SELECT name FROM users WHERE id={id}'.format(id=user_id)):
            self.cursor.execute('UPDATE users'
                                f" SET name = '{name}'"
                                f" WHERE id = '{user_id}'")
        else:
            self.add_info('users', ['id', 'name'], [user_id, name])

    @connect_close_decorator
    def get_user_name(self, person_id):

        """This method is returning persons name
        - id - persons id number"""
        if self.cursor.execute(f'SELECT name FROM users WHERE id={person_id}').fetchall():
            a = self.cursor.execute(f'SELECT name FROM users WHERE id={person_id}').fetchall()
            return self.unzip(a)[0]
        else:
            print('We haven`t your name in our database, please enter it')
            return False

    @connect_close_decorator
    def add_event(self, course_name, event_name):
        course_id = self.get_course_id(course_name)
        self.connect()
        self.cursor.execute(
            f"INSERT OR IGNORE INTO events (course_id, name) VALUES ({course_id}, '{event_name}')")
        print(
            f"INSERT OR IGNORE INTO events (course_id, name) VALUES ({course_id}, '{event_name}')")

    @connect_close_decorator
    def delete_event(self, event_name):
        event_id = self.get_event_id(event_name)
        self.connect()

        self.cursor.execute(f"DELETE FROM bookings WHERE event_id = {event_id}")
        self.cursor.execute(f"DELETE FROM events WHERE id = {event_id}")

    @connect_close_decorator
    def get_event_queue(self, event_id):
        result = self.cursor.execute(
            f"SELECT bookings.number,  users.name FROM bookings JOIN users ON users.id = bookings.user_id  WHERE "
            f"event_id={event_id} ORDER BY number").fetchall()
        return result

    @connect_close_decorator
    def is_user_present(self, user_id):
        result = self.cursor.execute(f"SELECT COUNT(name) FROM users WHERE id = {user_id}").fetchall()
        if result[0][0] == 0: return False
        return True

    @connect_close_decorator
    def delete_course(self, course_name):
        self.cursor.execute(f"DELETE FROM courses WHERE name = '{course_name}'")

    @connect_close_decorator
    def get_users(self):
        result = self.cursor.execute("SELECT * FROM users").fetchall()
        return result

    @connect_close_decorator
    def get_event_name(self, event_id):
        result = self.cursor.execute(f"SELECT name FROM events WHERE id = {event_id}").fetchall()
        return result[0][0]







