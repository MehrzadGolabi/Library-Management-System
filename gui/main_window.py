import sys
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                             QLabel, QApplication)
from gui.views.book_view import BookView
from gui.views.member_view import MemberView
from gui.views.loan_view import LoanView
from gui.views.report_view import ReportView
from gui.views.dashboard_view import DashboardView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.resize(1000, 700)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Implementation widgets
        self.dashboard_view = DashboardView()
        self.books_view = BookView()
        self.members_view = MemberView()
        self.loans_view = LoanView()
        self.reports_view = ReportView()

        # Add tabs
        self.tabs.addTab(self.dashboard_view, "Dashboard")
        self.tabs.addTab(self.books_view, "Books")
        self.tabs.addTab(self.members_view, "Members")
        self.tabs.addTab(self.loans_view, "Loans")
        self.tabs.addTab(self.reports_view, "Reports")

    def _setup_placeholder(self, widget, text):
        layout = QVBoxLayout(widget)
        label = QLabel(text)
        layout.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
