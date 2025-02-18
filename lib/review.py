from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

import sqlite3
class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError(
                "year must be an integer >= 2000"
            )

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError(
                "summary must be a non-empty string"
            )

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id):
        if type(employee_id) is int and Employee.find_by_id(employee_id):
            self._employee_id = employee_id
        else:
            raise ValueError(
                "employee_id must reference an employee in the database")

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )


    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        try:
            sql = """
                INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)
            """
            cursor = CONN.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = cursor.lastrowid
            type(self).all[self.id] = self
        except sqlite3.Error as e:
            print("hello")
            CONN.rollback()
            import ipdb; ipdb.set_trace()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database """
        rev = cls(year, summary, employee_id)
        rev.save()
        return rev
    
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review object having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        # review = cls.all.get(row[0])
        if review:= cls.all.get(row[0]):
            review.year, review.summary, review.employee_id = row[1], row[2], row[3]
        else:
            review = cls(row[1], row[2], row[3], row[0])
            cls.all[review.id] = review
        return review
    

    @classmethod
    def find_by_id(cls, id):
        """Return a Review object having the attribute values from the table row."""
        sql = """
            SELECT * FROM reviews
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone() 
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review object."""
        sql = """
            UPDATE reviews
            SET year = ?,
            summary = ?,
            employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the row corresponding to the current Review object"""
        sql = """
            DELETE FROM reviews
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Delete the dictionary entry using id as the key
        del type(self).all[self.id]

        # Set the id to None
        #! Line 159 breaks a test but think about it
        #! If there were an object representation of the record you just deleted
        #! Would you want that record to retain its id? Or should it be set to None?
        # self.id = None

    @classmethod
    def get_all(cls):
        """Return a list containing one Review object per table row"""
        sql = """
            SELECT * FROM reviews;
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def employee(self): #! belongs_to
        from employee import Employee
        return Employee.find_by_id(self.employee_id) if self.employee_id else None