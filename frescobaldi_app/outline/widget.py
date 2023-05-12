# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The document outline tool widget.
"""

from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtGui import QBrush, QFont, QTextCursor, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

import app
import qutil
import cursortools
import tokeniter
import documentstructure

import qtawesome as qta


class Widget(QTreeWidget):
    def __init__(self, tool):
        super(Widget, self).__init__(tool, headerHidden=True)
        self._timer = QTimer(singleShot=True, timeout=self.updateView)
        tool.mainwindow().currentDocumentChanged.connect(self.slotCurrentDocumentChanged)
        self.itemClicked.connect(self.slotItemClicked)
        self.itemActivated.connect(self.slotItemClicked)
        self.itemCollapsed.connect(self.slotItemCollapsed)
        self.itemExpanded.connect(self.slotItemExpanded)
        app.settingsChanged.connect(self.updateView)
        doc = tool.mainwindow().currentDocument()
        if doc:
            self.slotCurrentDocumentChanged(doc)

    def slotCurrentDocumentChanged(self, doc, old=None):
        """Called whenever the mainwindow changes the current document."""
        if old:
            old.contentsChange.disconnect(self.slotContentsChange)
        if doc:
            doc.contentsChange.connect(self.slotContentsChange)
            self._timer.start(100)

    def slotContentsChange(self, position, added, removed):
        """Updates the view on contents change."""
        if added + removed > 1000:
            self._timer.start(100)
        else:
            self._timer.start(2000)

    def updateView(self):
        """Recreate the items in the view."""
        with qutil.signalsBlocked(self):
            self.clear()
            doc = self.parent().mainwindow().currentDocument()
            if not doc:
                return

            view_cursor_position = self.parent().mainwindow().textCursor().position()
            structure = documentstructure.DocumentStructure.instance(doc)
            last_item = None
            current_item = None
            last_block = None

            for outline_item in structure.outline():
                position = outline_item.start()
                block = doc.findBlock(position)
                depth = tokeniter.state(block).depth()

                if block == last_block:
                    parent = last_item
                elif last_block is None or depth == 1:
                    # a toplevel item anyway
                    parent = self
                else:
                    while last_item and depth <= last_item.depth:
                        last_item = last_item.parent()
                    if not last_item:
                        parent = self
                    else:
                        # the item could belong to a parent item, but see if they
                        # really are in the same (toplevel) state
                        b = last_block.next()
                        while b < block:
                            depth2 = tokeniter.state(b).depth()
                            if depth2 == 1:
                                parent = self
                                break
                            while last_item and depth2 <= last_item.depth:
                                last_item = last_item.parent()
                            if not last_item:
                                parent = self
                                break
                            b = b.next()
                        else:
                            parent = last_item

                item = last_item = QTreeWidgetItem(parent)

                # set item text and display style bold if 'title' was used
                for name, text in outline_item.groupdict().items():
                    if text:
                        if name.startswith("new"):
                            if 'Staff' in text:
                                name = 'staff'
                                text = 'Staff'
                            style_item(item, name, text)
                            break
                        elif name.startswith("decl"):
                            declaration = block.text()[len(text):].lstrip()

                            if declaration.startswith(r'\lyr'):
                                name = 'lyric'
                            elif declaration.startswith(r'\markup'):
                                name = 'markup'
                            elif declaration.startswith(r'#('):
                                name = 'scm'
                            elif declaration.startswith(r'\fig'):
                                name = 'figures'
                            elif declaration.startswith(r'\rel'):
                                name = 'relative'
                            else:
                                name = 'declaration'

                            text = text[:-1]  # remove equals sign
                            style_item(item, name, text)
                            break
                        elif name.startswith('alert'):
                            text = outline_item.group('id') + " [" + outline_item.group('caption')[1:] + "]"
                            style_item(item, name, text)
                            break
                        else:
                            style_item(item, name, text)
                            break
                    else:
                        text = outline_item.group()

                    # item.setText(0, text)

                # remember whether it was collapsed by the user
                try:
                    collapsed = block.userData().collapsed
                except AttributeError:
                    collapsed = False
                item.setExpanded(not collapsed)
                item.depth = depth
                item.position = position
                last_block = block
                # scroll to the item at the view's cursor later
                if position <= view_cursor_position:
                    current_item = item
            if current_item:
                self.scrollToItem(current_item)

    def cursorForItem(self, item):
        """Returns a cursor for the specified item.

        This method (as all others) assume that the item refers to the current
        Document.

        """
        doc = self.parent().mainwindow().currentDocument()
        cursor = QTextCursor(doc)
        cursor.setPosition(item.position)
        return cursor

    def slotItemClicked(self, item):
        """Called when the user clicks an item."""
        item.setSelected(True)
        cursor = self.cursorForItem(item)
        cursor.movePosition(cursor.StartOfBlock)
        import browseriface
        browseriface.get(self.parent().mainwindow()).setTextCursor(cursor)
        view = self.parent().mainwindow().currentView()
        view.centerCursor()
        view.setFocus()

    def slotItemCollapsed(self, item):
        """Called when the user collapses an item."""
        block = self.cursorForItem(item).block()
        cursortools.data(block).collapsed = True

    def slotItemExpanded(self, item):
        """Called when the user expands an item."""
        block = self.cursorForItem(item).block()
        cursortools.data(block).collapsed = False

    def event(self, ev):
        """Reimplemented to show custom tool tips."""
        if ev.type() == QEvent.ToolTip:
            i = self.indexAt(ev.pos() - self.viewport().pos())
            item = self.itemFromIndex(i)
            if item:
                self.showToolTip(item)
                return True
        return super(Widget, self).event(ev)

    def showToolTip(self, item):
        """Called when a tool tip for the specified item needs to be shown."""
        import documenttooltip
        documenttooltip.show(self.cursorForItem(item))


from . import _outline_styles

_qta_cache = {}
_color_cache = {}


def cached_value(cache, key, supplier):
    """
    Return the value associated to the key in the dictionary, if present, else calculate the value through the supplier
    function and store the value in the cache.
    :param cache: A dictionary
    :param key:
    :param supplier: A function that supply a value for a given key
    :return:
    """
    if key in cache.keys():
        return cache[key]
    else:
        value = supplier(key)
        cache[key] = value
        return value


def color(style):
    return QBrush(QColor(style[TEXT_COLOR]))


def style_item(tree_item: QTreeWidgetItem, name, text):
    try:
        style = _outline_styles[name]
    except KeyError:
        style = _outline_styles['default']

    font: QFont = tree_item.font(0)
    font.setBold(style[BOLD])
    font.setItalic(style[ITALIC])
    font.setUnderline(style[UNDERLINE])
    tree_item.setFont(0, font)
    tree_item.setForeground(0, cached_value(_color_cache, name, lambda key: color(style)))  # text color
    tree_item.setText(0, style[DISPLAY_VALUE] if style[DISPLAY_VALUE] else text)

    # TODO cache
    if style[FA_ICON]:
        if name in _qta_cache.keys():
            tree_item.setIcon(0, _qta_cache[name])
        else:
            icon = qta.icon(style[FA_ICON], color=style[ICON_COLOR])
            tree_item.setIcon(0, icon)
            _qta_cache[name] = icon


BOLD = 'bold'
ITALIC = 'italic'
UNDERLINE = 'underline'
DISPLAY_VALUE = 'display-value'
ICON_COLOR = 'icon-color'
FA_ICON = 'fa-icon'
TEXT_COLOR = 'text-color'
