from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableView, QHeaderView, QDialog, 
                             QFormLayout, QMessageBox, QLabel)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.loan import Loan
from models.book import Book
from models.member import Member
from controllers.loan_controller import LoanController
from datetime import date

class LoanTableModel(QAbstractTableModel):
    def __init__(self, loans=None):
        super().__init__()
        self._loans = loans or []
        self._headers = ["ID", "Member", "Book", "Loan Date", "Due Date", "Status"]

    def rowCount(self, parent=None):
        return len(self._loans)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        
        loan = self._loans[index.row()]
        col = index.column()
        
        if col == 0: return loan.id
        elif col == 1: 
            member = Member.get_by_id(loan.member_id)
            return member.name if member else f"ID: {loan.member_id}"
        elif col == 2: 
            book = Book.get_by_id(loan.book_id)
            return book.title if book else f"ID: {loan.book_id}"
        elif col == 3: return loan.loan_date
        elif col == 4: return loan.due_date
        elif col == 5: return "Returned" if loan.return_date else "Active"
        return None

    def update_data(self, loans):
        self.beginResetModel()
        self._loans = loans
        self.endResetModel()

class IssueLoanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Issue New Loan")
        self.layout = QFormLayout(self)

        self.mid_input = QLineEdit()
        self.bid_input = QLineEdit()

        self.layout.addRow("Member ID:", self.mid_input)
        self.layout.addRow("Book ID:", self.bid_input)

        self.submit_btn = QPushButton("Issue Loan")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {
            "member_id": self.mid_input.text(),
            "book_id": self.bid_input.text()
        }

class LoanView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.controller = LoanController()

        # Toolbar
        self.toolbar = QHBoxLayout()
        
        self.issue_btn = QPushButton("Issue Loan")
        self.issue_btn.clicked.connect(self.open_issue_dialog)
        
        self.return_btn = QPushButton("Return Selected Book")
        self.return_btn.clicked.connect(self.return_book)
        
        self.toolbar.addWidget(self.issue_btn)
        self.toolbar.addWidget(self.return_btn)
        self.layout.addLayout(self.toolbar)

        # Table
        self.table_view = QTableView()
        self.model = LoanTableModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table_view)

        self.refresh_data()

    def refresh_data(self):
        # Fetch only active loans for the main view
        loans = Loan.get_active_loans()
        self.model.update_data(loans)

    def open_issue_dialog(self):
        dialog = IssueLoanDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                mid = int(data['member_id'])
                bid = int(data['book_id'])
                
                result = self.controller.issue_loan(mid, bid)
                if result['success']:
                    QMessageBox.information(self, "Success", result['message'])
                    self.refresh_data()
                else:
                    QMessageBox.warning(self, "Failed", result['message'])
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid ID format")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def return_book(self):
        indexes = self.table_view.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Warning", "Please select a loan to return.")
            return
        
        # Get loan object from model
        row = indexes[0].row()
        loan = self.model._loans[row]
        
        try:
            # Calculate fine
            fine = self.controller.calculate_fine(loan.due_date, date.today())
            
            msg = "Confirm return?"
            if fine > 0:
                msg += f"\n\nOVERDUE! Fine Amount: ${fine:.2f}"
            
            reply = QMessageBox.question(self, "Confirm Return", msg, 
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                loan.return_date = date.today()
                loan.fine_amount = fine
                loan.save()
                QMessageBox.information(self, "Success", "Book returned successfully.")
                self.refresh_data()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to return book: {e}")
