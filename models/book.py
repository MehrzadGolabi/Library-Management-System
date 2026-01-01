from database_manager import BaseEntity

class Book(BaseEntity):
    def __init__(self, title, isbn, category, publisher, shelf_location, 
                 publish_year=None, quantity=0, id=None):
        super().__init__()
        self.id = id
        self.title = title
        self.isbn = isbn
        self.category = category
        self.publisher = publisher
        self.publish_year = publish_year
        self.shelf_location = shelf_location
        self.quantity = quantity

    def save(self):
        if self.id:
            sql = """UPDATE books SET title=%s, isbn=%s, category=%s, publisher=%s, 
                     publish_year=%s, shelf_location=%s, quantity=%s WHERE id=%s"""
            params = (self.title, self.isbn, self.category, self.publisher, 
                      self.publish_year, self.shelf_location, self.quantity, self.id)
            self.execute_query(sql, params)
        else:
            sql = """INSERT INTO books (title, isbn, category, publisher, 
                     publish_year, shelf_location, quantity) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            params = (self.title, self.isbn, self.category, self.publisher, 
                      self.publish_year, self.shelf_location, self.quantity)
            self.id = self.execute_query(sql, params)

    def add_author(self, author_id):
        sql = "INSERT IGNORE INTO book_authors (book_id, author_id) VALUES (%s, %s)"
        self.execute_query(sql, (self.id, author_id))

    @classmethod
    def get_by_id(cls, book_id):
        instance = cls("", "", "", "", "")
        sql = """SELECT id, title, isbn, category, publisher, publish_year, 
                        shelf_location, quantity FROM books WHERE id = %s"""
        result = instance.fetch_data(sql, (book_id,))
        if result:
            row = result[0]
            return cls(id=row[0], title=row[1], isbn=row[2], category=row[3], 
                       publisher=row[4], publish_year=row[5], 
                       shelf_location=row[6], quantity=row[7])
        return None

    @classmethod
    def get_by_isbn(cls, isbn):
        instance = cls("", "", "", "", "")
        sql = """SELECT id, title, isbn, category, publisher, publish_year, 
                        shelf_location, quantity FROM books WHERE isbn = %s"""
        result = instance.fetch_data(sql, (isbn,))
        if result:
            row = result[0]
            return cls(id=row[0], title=row[1], isbn=row[2], category=row[3], 
                       publisher=row[4], publish_year=row[5], 
                       shelf_location=row[6], quantity=row[7])
        return None

    @classmethod
    def search_by_title(cls, title):
        instance = cls("", "", "", "", "")
        sql = """SELECT id, title, isbn, category, publisher, publish_year, 
                        shelf_location, quantity FROM books WHERE title LIKE %s"""
        results = instance.fetch_data(sql, (f"%{title}%",))
        books = []
        for row in results:
            books.append(cls(id=row[0], title=row[1], isbn=row[2], category=row[3], 
                             publisher=row[4], publish_year=row[5], 
                             shelf_location=row[6], quantity=row[7]))
        return books

    @classmethod
    def get_all(cls):
        instance = cls("", "", "", "", "")
        sql = """SELECT id, title, isbn, category, publisher, publish_year, 
                        shelf_location, quantity FROM books ORDER BY shelf_location"""
        results = instance.fetch_data(sql)
        books = []
        for row in results:
            books.append(cls(id=row[0], title=row[1], isbn=row[2], category=row[3], 
                             publisher=row[4], publish_year=row[5], 
                             shelf_location=row[6], quantity=row[7]))
        return books
