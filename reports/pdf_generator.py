from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import date
from models.book import Book
from models.loan import Loan
from models.member import Member

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def _create_basic_table(self, data, header_color=colors.grey):
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return t

    def generate_inventory_report(self, filename="inventory_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        elements.append(Paragraph("Library Inventory Report", self.styles['Title']))
        elements.append(Paragraph(f"Date: {date.today()}", self.styles['Normal']))
        elements.append(Spacer(1, 12))

        books = Book.get_all()
        data = [["ID", "Title", "ISBN", "Category", "Shelf", "Qty"]]
        for b in books:
            data.append([b.id, b.title, b.isbn, b.category, b.shelf_location, b.quantity])

        elements.append(self._create_basic_table(data))
        doc.build(elements)
        return filename

    def generate_overdue_report(self, filename="overdue_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        elements.append(Paragraph("Overdue Loans Report", self.styles['Title']))
        elements.append(Paragraph(f"Date: {date.today()}", self.styles['Normal']))
        elements.append(Spacer(1, 12))

        loans = Loan.get_overdue_loans()
        data = [["Loan ID", "Member", "Book ID", "Due Date", "Days Late"]]
        for l in loans:
            member = Member.get_by_id(l.member_id)
            member_name = member.name if member else f"ID: {l.member_id}"
            days_late = (date.today() - l.due_date).days
            data.append([l.id, member_name, l.book_id, l.due_date, days_late])

        elements.append(self._create_basic_table(data, colors.red))
        doc.build(elements)
        return filename

    def generate_active_loans_report(self, filename="active_loans_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        elements.append(Paragraph("Active Loans Report", self.styles['Title']))
        elements.append(Paragraph(f"Date: {date.today()}", self.styles['Normal']))
        elements.append(Spacer(1, 12))

        loans = Loan.get_active_loans()
        data = [["Loan ID", "Member", "Book Title", "Loan Date", "Due Date"]]
        for l in loans:
            member = Member.get_by_id(l.member_id)
            book = Book.get_by_id(l.book_id)
            
            member_name = member.name if member else f"ID: {l.member_id}"
            book_title = book.title if book else f"ID: {l.book_id}"
            
            data.append([l.id, member_name, book_title, l.loan_date, l.due_date])

        elements.append(self._create_basic_table(data, colors.blue))
        doc.build(elements)
        return filename

    def generate_member_report(self, filename="member_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        elements.append(Paragraph("Member Directory", self.styles['Title']))
        elements.append(Paragraph(f"Date: {date.today()}", self.styles['Normal']))
        elements.append(Spacer(1, 12))

        members = Member.get_all()
        data = [["ID", "Name", "National ID", "Phone", "Join Date"]]
        for m in members:
            data.append([m.id, m.name, m.national_id, m.phone, m.join_date])

        elements.append(self._create_basic_table(data, colors.green))
        doc.build(elements)
        return filename