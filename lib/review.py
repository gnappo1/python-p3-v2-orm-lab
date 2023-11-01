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
        return Employee.find_by_id(self.employee_id)