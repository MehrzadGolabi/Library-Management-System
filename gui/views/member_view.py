from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QTableView, QHeaderView, QDialog, 
                             QFormLayout, QMessageBox)
from PySide6.QtCore import Qt, QAbstractTableModel
from models.member import Member

class MemberTableModel(QAbstractTableModel):
    def __init__(self, members=None):
        super().__init__()
        self._members = members or []
        self._headers = ["ID", "Name", "National ID", "Phone", "Joined"]

    def rowCount(self, parent=None):
        return len(self._members)

    def columnCount(self, parent=None):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def data(self, index, role):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        
        member = self._members[index.row()]
        col = index.column()
        
        if col == 0: return member.id
        elif col == 1: return member.name
        elif col == 2: return member.national_id
        elif col == 3: return member.phone
        elif col == 4: return member.join_date
        return None

    def update_data(self, members):
        self.beginResetModel()
        self._members = members
        self.endResetModel()

class RegisterMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register New Member")
        self.layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.nid_input = QLineEdit()
        self.phone_input = QLineEdit()

        self.layout.addRow("Full Name:", self.name_input)
        self.layout.addRow("National ID:", self.nid_input)
        self.layout.addRow("Phone:", self.phone_input)

        self.submit_btn = QPushButton("Register")
        self.submit_btn.clicked.connect(self.accept)
        self.layout.addRow(self.submit_btn)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "national_id": self.nid_input.text(),
            "phone": self.phone_input.text()
        }

class MemberView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        # Toolbar
        self.toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.textChanged.connect(self.search_members)
        
        self.reg_btn = QPushButton("Register Member")
        self.reg_btn.clicked.connect(self.open_register_dialog)
        
        self.toolbar.addWidget(self.search_input)
        self.toolbar.addWidget(self.reg_btn)
        self.layout.addLayout(self.toolbar)

        # Table
        self.table_view = QTableView()
        self.model = MemberTableModel()
        self.table_view.setModel(self.model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table_view)

        self.refresh_data()

    def refresh_data(self):
        members = Member.get_all()
        self.model.update_data(members)

    def search_members(self):
        text = self.search_input.text()
        if not text:
            self.refresh_data()
            return
        members = Member.search_by_name(text)
        self.model.update_data(members)

    def open_register_dialog(self):
        dialog = RegisterMemberDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                member = Member(
                    name=data['name'],
                    national_id=data['national_id'],
                    phone=data['phone']
                )
                member.save()
                QMessageBox.information(self, "Success", f"Member registered with ID: {member.id}")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to register member: {e}")
