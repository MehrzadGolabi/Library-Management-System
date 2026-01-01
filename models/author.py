from database_manager import BaseEntity

class Author(BaseEntity):
    def __init__(self, name, id=None):
        super().__init__()
        self.id = id
        self.name = name

    def save(self):
        if self.id:
            sql = "UPDATE authors SET name = %s WHERE id = %s"
            params = (self.name, self.id)
            self.execute_query(sql, params)
        else:
            sql = "INSERT INTO authors (name) VALUES (%s)"
            params = (self.name,)
            self.id = self.execute_query(sql, params)

    @classmethod
    def get_by_id(cls, author_id):
        # Create a temp instance to use fetch_data or use a static/class method approach
        instance = cls(name="")
        sql = "SELECT id, name FROM authors WHERE id = %s"
        result = instance.fetch_data(sql, (author_id,))
        if result:
            return cls(id=result[0][0], name=result[0][1])
        return None
