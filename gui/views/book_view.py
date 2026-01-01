from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableView, QHeaderView, QDialog, 
                             QFormLayout, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.book import Book
from models.author import Author

class BookTableModel(QAbstractTableModel):
    def __init__(self, books=None):
        super().__init__()
        self._books = books or []
        self._headers = ["ID", "Title", "ISBN", "Category", "Shelf", "Qty"]

    def rowCount(self, parent=None):
        return len(self._books)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        
        book = self._books[index.row()]
        col = index.column()
        
        if col == 0: return book.id
        elif col == 1: return book.title
        elif col == 2: return book.isbn
        elif col == 3: return book.category
        elif col == 4: return book.shelf_location
        elif col == 5: return book.quantity
        return None

    def update_data(self, books):
        self.beginResetModel()
        self._books = books
        self.endResetModel()

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Book")
        self.layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.isbn_input = QLineEdit()
        self.category_input = QLineEdit()
        self.publisher_input = QLineEdit()
        self.shelf_input = QLineEdit()
        self.qty_input = QLineEdit()
        self.authors_input = QLineEdit()

        self.layout.addRow("Title:", self.title_input)
        self.layout.addRow("ISBN:", self.isbn_input)
        self.layout.addRow("Category:", self.category_input)
        self.layout.addRow("Publisher:", self.publisher_input)
        self.layout.addRow("Shelf Location:", self.shelf_input)
        self.layout.addRow("Quantity:", self.qty_input)
        self.layout.addRow("Authors (comma sep):", self.authors_input)

        self.submit_btn = QPushButton("Save")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {
            "title": self.title_input.text(),
            "isbn": self.isbn_input.text(),
            "category": self.category_input.text(),
            "publisher": self.publisher_input.text(),
            "shelf": self.shelf_input.text(),
            "qty": self.qty_input.text(),
            "authors": self.authors_input.text()
        }

class BookView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Toolbar
        self.toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title...")
        self.search_input.textChanged.connect(self.search_books)
        
        self.add_btn = QPushButton("Add Book")
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        self.toolbar.addWidget(self.search_input)
        self.toolbar.addWidget(self.add_btn)
        self.layout.addLayout(self.toolbar)

        # Table
        self.table_view = QTableView()
        self.model = BookTableModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table_view)

        self.refresh_data()

    def refresh_data(self):
        books = Book.get_all()
        self.model.update_data(books)

    def search_books(self):
        text = self.search_input.text()
        if not text:
            self.refresh_data()
            return
        books = Book.search_by_title(text)
        self.model.update_data(books)

    def open_add_dialog(self):
        dialog = AddBookDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                book = Book(
                    title=data['title'],
                    isbn=data['isbn'],
                    category=data['category'],
                    publisher=data['publisher'],
                    shelf_location=data['shelf'],
                    quantity=int(data['qty']) if data['qty'] else 0
                )
                book.save()
                
                # Handle authors
                author_names = data['authors'].split(',')
                for name in author_names:
                    name = name.strip()
                    if name:
                        author = Author(name=name)
                        author.save()
                        book.add_author(author.id)
                
                QMessageBox.information(self, "Success", "Book added successfully!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add book: {e}")
