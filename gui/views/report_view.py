from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QMessageBox, QGroupBox)
from reports.pdf_generator import PDFGenerator
from gui.pdf_viewer import PDFViewerWindow
import os

class ReportView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.pdf_gen = PDFGenerator()
        self.viewers = []  # Keep references to prevent garbage collection

        self.layout.addWidget(QLabel("<h2>Generate Reports</h2>"))

        # Group for PDF Actions
        group = QGroupBox("PDF Reports")
        group_layout = QVBoxLayout()

        self.btn_inventory = QPushButton("Generate Inventory Report")
        self.btn_overdue = QPushButton("Generate Overdue Loans Report")
        self.btn_active = QPushButton("Generate Active Loans Report")
        self.btn_members = QPushButton("Generate Member Directory")

        self.btn_inventory.clicked.connect(lambda: self.generate_report("inventory"))
        self.btn_overdue.clicked.connect(lambda: self.generate_report("overdue"))
        self.btn_active.clicked.connect(lambda: self.generate_report("active"))
        self.btn_members.clicked.connect(lambda: self.generate_report("members"))

        group_layout.addWidget(self.btn_inventory)
        group_layout.addWidget(self.btn_overdue)
        group_layout.addWidget(self.btn_active)
        group_layout.addWidget(self.btn_members)
        
        group.setLayout(group_layout)
        self.layout.addWidget(group)
        self.layout.addStretch()

    def generate_report(self, report_type):
        try:
            filename = ""
            if report_type == "inventory":
                filename = self.pdf_gen.generate_inventory_report()
            elif report_type == "overdue":
                filename = self.pdf_gen.generate_overdue_report()
            elif report_type == "active":
                filename = self.pdf_gen.generate_active_loans_report()
            elif report_type == "members":
                filename = self.pdf_gen.generate_member_report()
            
            # Show the PDF Viewer automatically
            viewer = PDFViewerWindow(self)
            viewer.open_pdf(filename)
            viewer.show()
            self.viewers.append(viewer)
            # Cleanup closed viewers
            self.viewers = [v for v in self.viewers if v.isVisible() or v.isEnabled()]
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")
