import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QTextDocument, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeWidgetItem, QTreeWidget

import ly.document
from frescobaldi_app import toplevel
from ly.docinfo import DocInfo

toplevel.install()

import tokeniter, qutil
from documentstructure import outline_re, DocumentStructure
import time

dir = r'G:\Il mio Drive\Frescobaldi Projects\Rusca\Missa A19-21'
missa = os.path.join(dir, 'credo.ly')

t = time.time()
missa = open(missa, 'r', encoding='utf-8')
text = missa.read()
missa.close()
t = time.time() - t
print(t)
doc = ly.document.Document(text)
qDoc = QTextDocument()
c = QTextCursor(qDoc)
c.insertText(text)

t = time.time()
outline_list = list(outline_re(False).finditer(text))
# match patterns including comments
# outline_list_comments = list(outline_re(True).finditer(self.document().toPlainText()))
# merge lists and sort by start position
outline_list.sort(key=lambda match: match.start())
t = time.time() - t
print(t)

app = QApplication([])
w = QWidget(flags=Qt.Widget)
tree = QTreeWidget()
tree.setColumnCount(1)
tree.setHeaderHidden(True)
layout = QVBoxLayout()
layout.addWidget(tree)
w.setLayout(layout)

import scanner

scanner.structure(tree)
tree.expandAll()
w.show()

app.exec()
