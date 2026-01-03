from __future__ import annotations
import math
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (QMainWindow, QToolBar, QSpinBox, QComboBox, 
                               QVBoxLayout, QWidget, QStatusBar)
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QUrl, Slot, Signal, QPoint

class ZoomSelector(QComboBox):
    zoom_mode_changed = Signal(QPdfView.ZoomMode)
    zoom_factor_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.addItem("Fit Width")
        self.addItem("Fit Page")
        self.addItem("25%")
        self.addItem("50%")
        self.addItem("75%")
        self.addItem("100%")
        self.addItem("125%")
        self.addItem("150%")
        self.addItem("200%")
        self.addItem("400%")
        self.setCurrentIndex(5)  # 100%
        
        self.currentTextChanged.connect(self.on_text_changed)
        self.lineEdit().editingFinished.connect(self._editing_finished)

    @Slot()
    def reset(self):
        self.setCurrentIndex(5)  # 100%

    @Slot()
    def _editing_finished(self):
        self.on_text_changed(self.lineEdit().text())

    @Slot(float)
    def set_zoom_factor(self, factor: float):
        percent = int(factor * 100)
        self.setCurrentText(f"{percent}%")

    @Slot(str)
    def on_text_changed(self, text: str):
        if text == "Fit Width":
            self.zoom_mode_changed.emit(QPdfView.ZoomMode.FitToWidth)
        elif text == "Fit Page":
            self.zoom_mode_changed.emit(QPdfView.ZoomMode.FitInView)
        elif text.endswith("%"):
            try:
                zoom_level = int(text[:-1])
                factor = zoom_level / 100.0
                self.zoom_mode_changed.emit(QPdfView.ZoomMode.Custom)
                self.zoom_factor_changed.emit(factor)
            except ValueError:
                pass

class PDFViewerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Report Viewer")
        self.resize(1000, 800)
        
        self.m_document = QPdfDocument(self)
        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.m_document)
        
        self.setCentralWidget(self.pdf_view)
        
        self.setup_ui()
        self.setup_signals()

    def setup_ui(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.addToolBar(self.toolbar)
        
        # Navigation
        self.action_prev = QAction(QIcon.fromTheme("go-previous"), "Previous", self)
        self.action_next = QAction(QIcon.fromTheme("go-next"), "Next", self)
        self.toolbar.addAction(self.action_prev)
        
        self.page_selector = QSpinBox(self)
        self.page_selector.setMinimum(1)
        self.page_selector.setPrefix("Page ")
        self.toolbar.addWidget(self.page_selector)
        
        self.toolbar.addAction(self.action_next)
        self.toolbar.addSeparator()
        
        # Zoom
        self.action_zoom_out = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
        self.action_zoom_in = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
        self.toolbar.addAction(self.action_zoom_out)
        
        self.zoom_selector = ZoomSelector(self)
        self.zoom_selector.setMinimumWidth(120)
        self.toolbar.addWidget(self.zoom_selector)
        
        self.toolbar.addAction(self.action_zoom_in)
        
        self.setStatusBar(QStatusBar(self))

    def setup_signals(self):
        self.action_prev.triggered.connect(self.prev_page)
        self.action_next.triggered.connect(self.next_page)
        self.page_selector.valueChanged.connect(self.goto_page)
        
        self.action_zoom_in.triggered.connect(self.zoom_in)
        self.action_zoom_out.triggered.connect(self.zoom_out)
        
        self.zoom_selector.zoom_mode_changed.connect(self.pdf_view.setZoomMode)
        self.zoom_selector.zoom_factor_changed.connect(self.pdf_view.setZoomFactor)
        
        nav = self.pdf_view.pageNavigator()
        nav.currentPageChanged.connect(self.sync_page_selector)
        
        self.pdf_view.zoomFactorChanged.connect(self.zoom_selector.set_zoom_factor)

    def open_pdf(self, file_path: str):
        if self.m_document.load(file_path):
            self.setWindowTitle(f"Report Viewer - {file_path}")
            self.page_selector.setMaximum(self.m_document.pageCount())
            self.page_selector.setValue(1)
            self.statusBar().showMessage(f"Loaded: {file_path}")
        else:
            self.statusBar().showMessage(f"Failed to load: {file_path}")

    @Slot()
    def prev_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() > 0:
            nav.jump(nav.currentPage() - 1, QPoint(), nav.currentZoom())

    @Slot()
    def next_page(self):
        nav = self.pdf_view.pageNavigator()
        if nav.currentPage() < self.m_document.pageCount() - 1:
            nav.jump(nav.currentPage() + 1, QPoint(), nav.currentZoom())

    @Slot(int)
    def goto_page(self, page_num: int):
        # QPdfView uses 0-based indexing, spinbox uses 1-based for users
        nav = self.pdf_view.pageNavigator()
        if 0 <= page_num - 1 < self.m_document.pageCount():
            nav.jump(page_num - 1, QPoint(), nav.currentZoom())

    @Slot(int)
    def sync_page_selector(self, page_index: int):
        self.page_selector.blockSignals(True)
        self.page_selector.setValue(page_index + 1)
        self.page_selector.blockSignals(False)

    @Slot()
    def zoom_in(self):
        factor = self.pdf_view.zoomFactor() * math.sqrt(2.0)
        self.pdf_view.setZoomFactor(factor)

    @Slot()
    def zoom_out(self):
        factor = self.pdf_view.zoomFactor() / math.sqrt(2.0)
        self.pdf_view.setZoomFactor(factor)
