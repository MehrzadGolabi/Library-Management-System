import sys
import os
from datetime import date, datetime
from tabulate import tabulate
from models.book import Book
from models.member import Member
from models.author import Author
from models.loan import Loan
from controllers.loan_controller import LoanController
from reports.pdf_generator import PDFGenerator

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{RESET}")

def print_success(text):
    print(f"{GREEN}SUCCESS: {text}{RESET}")

def print_error(text):
    print(f"{RED}ERROR: {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}WARNING: {text}{RESET}")

class LibraryCLI:
    def __init__(self):
        self.loan_controller = LoanController()
        self.pdf_gen = PDFGenerator()

    def main_menu(self):
        while True:
            print_header("LIBRARY MANAGEMENT SYSTEM")
            print("1. Book Management")
            print("2. Member Management")
            print("3. Loan Operations")
            print("4. Reports")
            print("5. Help")
            print("0. Exit")
            
            choice = input(f"\n{BOLD}Select an option: {RESET}")
            
            if choice == "1":
                self.book_menu()
            elif choice == "2":
                self.member_menu()
            elif choice == "3":
                self.loan_menu()
            elif choice == "4":
                self.report_menu()
            elif choice == "5":
                self.show_help()
            elif choice == "0":
                print_header("GOODBYE")
                sys.exit(0)
            else:
                print_error("Invalid option. Please try again.")

    # --- Book Management ---
    def book_menu(self):
        while True:
            print_header("BOOK MANAGEMENT")
            print("1. Add New Book")
            print("2. Search Book by Title")
            print("3. Search Book by ISBN")
            print("0. Back to Main Menu")
            
            choice = input(f"\n{BOLD}Select an option: {RESET}")
            if choice == "1":
                self.add_book()
            elif choice == "2":
                self.search_books_title()
            elif choice == "3":
                self.search_book_isbn()
            elif choice == "0":
                break
            else:
                print_error("Invalid option.")

    def add_book(self):
        print_header("ADD NEW BOOK")
        try:
            title = input("Title: ")
            isbn = input("ISBN: ")
            category = input("Category: ")
            publisher = input("Publisher: ")
            publish_year = input("Publish Year (optional): ")
            shelf = input("Shelf Location: ")
            qty = input("Quantity: ")
            
            book = Book(
                title=title, isbn=isbn, category=category, publisher=publisher,
                publish_year=int(publish_year) if publish_year else None,
                shelf_location=shelf, quantity=int(qty)
            )
            book.save()
            
            # Handle Authors
            author_names = input("Author(s) (comma separated): ").split(',')
            for name in author_names:
                name = name.strip()
                if not name: continue
                author = Author(name=name)
                author.save()
                book.add_author(author.id)
                
            print_success(f"Book '{title}' added successfully!")
        except Exception as e:
            print_error(f"Failed to add book: {e}")

    def search_books_title(self):
        title = input("Enter title keywords: ")
        books = Book.search_by_title(title)
        if not books:
            print_warning("No books found.")
            return
        
        data = [[b.id, b.title, b.isbn, b.category, b.shelf_location, b.quantity] for b in books]
        print(tabulate(data, headers=["ID", "Title", "ISBN", "Category", "Shelf", "Qty"], tablefmt="grid"))

    def search_book_isbn(self):
        isbn = input("Enter ISBN: ")
        book = Book.get_by_isbn(isbn)
        if not book:
            print_warning("Book not found.")
            return
        
        data = [[book.id, book.title, book.isbn, book.category, book.shelf_location, book.quantity]]
        print(tabulate(data, headers=["ID", "Title", "ISBN", "Category", "Shelf", "Qty"], tablefmt="grid"))

    # --- Member Management ---
    def member_menu(self):
        while True:
            print_header("MEMBER MANAGEMENT")
            print("1. Register New Member")
            print("2. Search Member by Name")
            print("0. Back to Main Menu")
            
            choice = input(f"\n{BOLD}Select an option: {RESET}")
            if choice == "1":
                self.add_member()
            elif choice == "2":
                self.search_members()
            elif choice == "0":
                break
            else:
                print_error("Invalid option.")

    def add_member(self):
        print_header("REGISTER MEMBER")
        try:
            name = input("Name: ")
            nid = input("National ID: ")
            phone = input("Phone: ")
            member = Member(name=name, national_id=nid, phone=phone)
            member.save()
            print_success(f"Member '{name}' registered successfully! ID: {member.id}")
        except Exception as e:
            print_error(f"Failed to register member: {e}")

    def search_members(self):
        name = input("Enter name: ")
        members = Member.search_by_name(name)
        if not members:
            print_warning("No members found.")
            return
        
        data = [[m.id, m.name, m.national_id, m.phone, m.join_date] for m in members]
        print(tabulate(data, headers=["ID", "Name", "National ID", "Phone", "Joined"], tablefmt="grid"))

    # --- Loan Operations ---
    def loan_menu(self):
        while True:
            print_header("LOAN OPERATIONS")
            print("1. Issue New Loan")
            print("2. Return Book")
            print("0. Back to Main Menu")
            
            choice = input(f"\n{BOLD}Select an option: {RESET}")
            if choice == "1":
                self.issue_loan()
            elif choice == "2":
                self.return_book()
            elif choice == "0":
                break
            else:
                print_error("Invalid option.")

    def issue_loan(self):
        print_header("ISSUE LOAN")
        try:
            mid = int(input("Member ID: "))
            
            book_input = input("Book ID or Title: ")
            bid = None
            
            if book_input.isdigit():
                bid = int(book_input)
            else:
                # Search by title
                books = Book.search_by_title(book_input)
                if not books:
                    print_error("No books found with that title.")
                    return
                elif len(books) == 1:
                    bid = books[0].id
                    print(f"Selected: {books[0].title} (ID: {bid})")
                else:
                    print_warning("Multiple books found:")
                    data = [[b.id, b.title, b.isbn] for b in books]
                    print(tabulate(data, headers=["ID", "Title", "ISBN"], tablefmt="grid"))
                    bid = int(input("Enter Book ID from list: "))

            result = self.loan_controller.issue_loan(mid, bid)
            if result['success']:
                print_success(result['message'])
            else:
                print_error(result['message'])
        except ValueError:
            print_error("Invalid ID format.")
        except Exception as e:
            print_error(f"Error: {e}")

    def return_book(self):
        print_header("RETURN BOOK")
        try:
            loan_id = int(input("Enter Loan ID: "))
            loan = Loan.get_by_id(loan_id)
            if not loan:
                print_error("Loan record not found.")
                return
            
            if loan.return_date:
                print_warning("This book has already been returned.")
                return

            fine = self.loan_controller.calculate_fine(loan.due_date, date.today())
            if fine > 0:
                print_warning(f"Book is overdue! Calculated Fine: ${fine:.2f}")
                confirm = input("Confirm return and payment of fine? (y/n): ")
                if confirm.lower() != 'y':
                    print("Return cancelled.")
                    return
            
            loan.return_date = date.today()
            loan.fine_amount = fine
            loan.save()
            print_success("Book returned successfully.")
            
        except ValueError:
            print_error("Invalid ID format.")
        except Exception as e:
            print_error(f"Error: {e}")

    # --- Reports ---
    def report_menu(self):
        while True:
            print_header("REPORTS")
            print("1. Generate Inventory PDF")
            print("2. Generate Overdue Loans PDF")
            print("3. Generate Active Loans PDF")
            print("4. Generate Member Directory PDF")
            print("0. Back to Main Menu")
            
            choice = input(f"\n{BOLD}Select an option: {RESET}")
            if choice == "1":
                fname = self.pdf_gen.generate_inventory_report()
                print_success(f"Inventory report saved to {os.path.abspath(fname)}")
            elif choice == "2":
                fname = self.pdf_gen.generate_overdue_report()
                print_success(f"Overdue report saved to {os.path.abspath(fname)}")
            elif choice == "3":
                fname = self.pdf_gen.generate_active_loans_report()
                print_success(f"Active loans report saved to {os.path.abspath(fname)}")
            elif choice == "4":
                fname = self.pdf_gen.generate_member_report()
                print_success(f"Member report saved to {os.path.abspath(fname)}")
            elif choice == "0":
                break
            else:
                print_error("Invalid option.")

    # --- Help ---
    def show_help(self):
        print_header("USER GUIDE & HELP")
        help_text = [
            ["Command", "Description"],
            ["Book Management", "Add books, link authors, and search the catalog."],
            ["Member Management", "Register new members and search existing ones."],
            ["Loan Operations", "Issue 7-day loans (max 1 per member) and process returns."],
            ["Fine Calculation", "Fines are $1.00/day for overdue returns."],
            ["Reports", "Generate professional PDFs for Inventory and Overdue lists."]
        ]
        print(tabulate(help_text, headers="firstrow", tablefmt="simple"))
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    app = LibraryCLI()
    try:
        app.main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
