from database_manager import BaseEntity
from datetime import date

class Member(BaseEntity):
    def __init__(self, name, national_id, phone=None, join_date=None, id=None):
        super().__init__()
        self.id = id
        self.name = name
        self.national_id = national_id
        self.phone = phone
        self.join_date = join_date or date.today()

    def save(self):
        if self.id:
            sql = "UPDATE members SET name=%s, national_id=%s, phone=%s, join_date=%s WHERE id=%s"
            params = (self.name, self.national_id, self.phone, self.join_date, self.id)
            self.execute_query(sql, params)
        else:
            sql = "INSERT INTO members (name, national_id, phone, join_date) VALUES (%s, %s, %s, %s)"
            params = (self.name, self.national_id, self.phone, self.join_date)
            self.id = self.execute_query(sql, params)

    @classmethod
    def get_by_id(cls, member_id):
        instance = cls("", "")
        sql = "SELECT id, name, national_id, phone, join_date FROM members WHERE id = %s"
        result = instance.fetch_data(sql, (member_id,))
        if result:
            row = result[0]
            return cls(id=row[0], name=row[1], national_id=row[2], 
                       phone=row[3], join_date=row[4])
        return None

    @classmethod
    def search_by_name(cls, name):
        instance = cls("", "")
        sql = "SELECT id, name, national_id, phone, join_date FROM members WHERE name LIKE %s"
        results = instance.fetch_data(sql, (f"%{name}%",))
        members = []
        for row in results:
            members.append(cls(id=row[0], name=row[1], national_id=row[2], 
                               phone=row[3], join_date=row[4]))
        return members

    @classmethod
    def get_all(cls):
        instance = cls("", "")
        sql = "SELECT id, name, national_id, phone, join_date FROM members"
        results = instance.fetch_data(sql)
        members = []
        for row in results:
            members.append(cls(id=row[0], name=row[1], national_id=row[2], 
                               phone=row[3], join_date=row[4]))
        return members
