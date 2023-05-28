import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush
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

t = time.time()
info = DocInfo(doc)
print(info.definitions())
print(info.markup_definitions())
t = time.time() - t
print(t)
# active_code = self.remove_comments()

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
layout = QVBoxLayout()
layout.addWidget(tree, alignment=Qt.AlignTop)
w.setLayout(layout)
w.show()

structure = DocumentStructure.instance(doc)
last_item = None
current_item = None
last_block = None
for i in structure.outline():
    position = i.start()
    block = doc.findBlock(position)
    depth = tokeniter.state(block).depth()
    if block == last_block:
        parent = last_item
    elif last_block is None or depth == 1:
        # a toplevel item anyway
        parent = tree
    else:
        while last_item and depth <= last_item.depth:
            last_item = last_item.parent()
        if not last_item:
            parent = tree
        else:
            # the item could belong to a parent item, but see if they
            # really are in the same (toplevel) state
            b = last_block.next()
            while b < block:
                depth2 = tokeniter.state(b).depth()
                if depth2 == 1:
                    parent = tree
                    break
                while last_item and depth2 <= last_item.depth:
                    last_item = last_item.parent()
                if not last_item:
                    parent = tree
                    break
                b = b.next()
            else:
                parent = last_item

    item = last_item = QTreeWidgetItem(parent)

    # set item text and display style bold if 'title' was used
    for name, text in i.groupdict().items():
        if text:
            if name.startswith('title'):
                font = item.font(0)
                font.setWeight(QFont.Bold)
                item.setFont(0, font)
                break
            elif name.startswith('alert'):
                color = item.foreground(0).color()
                color = qutil.addcolor(color, 128, 0, 0)
                item.setForeground(0, QBrush(color))
                font = item.font(0)
                font.setStyle(QFont.StyleItalic)
                item.setFont(0, font)
            elif name.startswith('text'):
                break
    else:
        text = i.group()
    item.setText(0, text)

    # remember whether is was collapsed by the user
    try:
        collapsed = block.userData().collapsed
    except AttributeError:
        collapsed = False
    item.setExpanded(not collapsed)
    item.depth = depth
    item.position = position
    last_block = block
app.exec()
