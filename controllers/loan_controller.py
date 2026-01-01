from datetime import date, timedelta
from models.loan import Loan

class LoanController:
    DAILY_FINE_RATE = 1.0

    def calculate_due_date(self, start_date):
        return start_date + timedelta(days=7)

    def calculate_fine(self, due_date, return_date):
        if return_date <= due_date:
            return 0.0
        overdue_days = (return_date - due_date).days
        return float(overdue_days * self.DAILY_FINE_RATE)

    def issue_loan(self, member_id, book_id):
        # 1. Check eligibility (Business Rule: 1 active loan)
        active_loans = Loan.get_active_loans_count(member_id)
        if active_loans >= 1:
            return {
                "success": False,
                "message": "Active loan limit reached (Max 1)."
            }

        # 2. Issue Loan
        # Note: This relies on Loan.issue_loan implementation later
        try:
            Loan.issue_loan(member_id, book_id)
            return {
                "success": True,
                "message": "Loan issued successfully."
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
