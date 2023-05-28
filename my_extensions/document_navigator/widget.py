import qutil
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QVBoxLayout, QTreeWidget, QTreeWidgetItem

# The mandatory import
from extensions.widget import ExtensionWidget

from .scanner import structure


class Widget(ExtensionWidget):
    """The Tool Panel widget."""

    def __init__(self, panel):
        super(Widget, self).__init__(panel)

        self.mainwindow().currentDocumentChanged.connect(self.document_changed)
        self.tree = tree = QTreeWidget()
        self.root = QTreeWidgetItem()
        tree.setHeaderHidden(True)
        tree.addTopLevelItem(self.root)
        index = tree.indexFromItem(self.root)
        tree.setRowHidden(0, index, True)
        layout = QVBoxLayout()
        layout.addWidget(tree)
        self.setLayout(layout)

        self.translateUI()

        doc = self.mainwindow().currentDocument()
        if doc:
            self.document_changed(doc)

    def document_changed(self, doc: QTextDocument, old: QTextDocument = None):
        # if old:
        #     old.contentsChange.disconnect(self.document_changed)
        # if doc:
        #     doc.contentsChange.connect(self.document_changed)

        with qutil.signalsBlocked(self):
            self.tree.clear()
            structure(self.tree, doc.toPlainText())
            self.tree.expandAll()

    def translateUI(self):
        pass
