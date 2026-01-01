from database_manager import BaseEntity
from datetime import date, timedelta

class Loan(BaseEntity):
    def __init__(self, member_id, book_id, loan_date=None, due_date=None, 
                 return_date=None, fine_amount=0.0, id=None):
        super().__init__()
        self.id = id
        self.member_id = member_id
        self.book_id = book_id
        self.loan_date = loan_date or date.today()
        self.due_date = due_date or (self.loan_date + timedelta(days=7))
        self.return_date = return_date
        self.fine_amount = fine_amount

    def save(self):
        if self.id:
            sql = """UPDATE loans SET member_id=%s, book_id=%s, loan_date=%s, 
                     due_date=%s, return_date=%s, fine_amount=%s WHERE id=%s"""
            params = (self.member_id, self.book_id, self.loan_date, 
                      self.due_date, self.return_date, self.fine_amount, self.id)
            self.execute_query(sql, params)
        else:
            sql = """INSERT INTO loans (member_id, book_id, loan_date, due_date, 
                     return_date, fine_amount) VALUES (%s, %s, %s, %s, %s, %s)"""
            params = (self.member_id, self.book_id, self.loan_date, 
                      self.due_date, self.return_date, self.fine_amount)
            self.id = self.execute_query(sql, params)

    @classmethod
    def get_active_loans_count(cls, member_id):
        instance = cls(0, 0)
        sql = "SELECT COUNT(*) FROM loans WHERE member_id = %s AND return_date IS NULL"
        result = instance.fetch_data(sql, (member_id,))
        if result:
            return result[0][0]
        return 0

    @classmethod
    def issue_loan(cls, member_id, book_id):
        loan = cls(member_id=member_id, book_id=book_id)
        loan.save()
        return loan

    @classmethod
    def get_by_id(cls, loan_id):
        instance = cls(0, 0)
        sql = """SELECT id, member_id, book_id, loan_date, due_date, return_date, 
                        fine_amount FROM loans WHERE id = %s"""
        result = instance.fetch_data(sql, (loan_id,))
        if result:
            row = result[0]
            return cls(id=row[0], member_id=row[1], book_id=row[2], 
                       loan_date=row[3], due_date=row[4], 
                       return_date=row[5], fine_amount=float(row[6]))
        return None
    @classmethod
    def get_overdue_loans(cls):
        instance = cls(0, 0)
        sql = """SELECT id, member_id, book_id, loan_date, due_date, return_date, 
                        fine_amount FROM loans 
                 WHERE return_date IS NULL AND due_date < CURDATE()"""
        results = instance.fetch_data(sql)
        loans = []
        for row in results:
            loans.append(cls(id=row[0], member_id=row[1], book_id=row[2], 
                             loan_date=row[3], due_date=row[4], 
                             return_date=row[5], fine_amount=float(row[6])))
        return loans

    @classmethod
    def get_active_loans(cls):
        instance = cls(0, 0)
        # return_date IS NULL
        sql = """SELECT id, member_id, book_id, loan_date, due_date, return_date, 
                        fine_amount FROM loans WHERE return_date IS NULL"""
        results = instance.fetch_data(sql)
        loans = []
        for row in results:
            loans.append(cls(id=row[0], member_id=row[1], book_id=row[2], 
                             loan_date=row[3], due_date=row[4], 
                             return_date=row[5], fine_amount=float(row[6])))
        return loans
        