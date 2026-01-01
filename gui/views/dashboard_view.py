from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QPushButton)
from PySide6.QtCore import Qt
from models.book import Book
from models.member import Member
from models.loan import Loan

class StatCard(QFrame):
    def __init__(self, title, value, color="#2196F3"):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                color: white;
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)
        layout = QVBoxLayout(self)
        
        lbl_value = QLabel(str(value))
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 14px;")
        
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_title)

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("<h2>Library Dashboard</h2>")
        self.layout.addWidget(header)

        # Stats Row
        self.stats_layout = QHBoxLayout()
        self.layout.addLayout(self.stats_layout)
        
        # Refresh Button
        self.refresh_btn = QPushButton("Refresh Stats")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        self.layout.addWidget(self.refresh_btn)
        self.layout.addStretch()

        self.refresh_stats()

    def refresh_stats(self):
        # Clear existing widgets in stats layout
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Fetch Data
        try:
            total_books = len(Book.get_all())
            total_members = len(Member.get_all())
            active_loans = len(Loan.get_active_loans())
            overdue_loans = len(Loan.get_overdue_loans())
        except Exception as e:
            print(f"Error fetching stats: {e}")
            total_books = "-"
            total_members = "-"
            active_loans = "-"
            overdue_loans = "-"

        # Add Cards
        self.stats_layout.addWidget(StatCard("Total Books", total_books, "#4CAF50"))
        self.stats_layout.addWidget(StatCard("Members", total_members, "#2196F3"))
        self.stats_layout.addWidget(StatCard("Active Loans", active_loans, "#FF9800"))
        self.stats_layout.addWidget(StatCard("Overdue", overdue_loans, "#F44336"))
