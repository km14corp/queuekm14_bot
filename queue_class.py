from Data_base.db_help_class import db_help


class queue:
    """This class for making your life easier, so you can use it to operate with queue with the 'name' how an object
    with it`s functions """
    def __init__(self, name):
        """The init method which create table with 'name' if it not exists"""
        self.name = name
        self.data_base = db_help('Data_base\\queue.db')
        self.data_base.make_db(self.name)

    def return_names(self):
        """This method will return list of names of this object"""
        self.data_base.return_names(self.name)

    def add_id(self, id):
        """This method is to add new person into the objects table
        - id - the persons tg id"""
        self.data_base.add_info(self.name, 'name', id)
