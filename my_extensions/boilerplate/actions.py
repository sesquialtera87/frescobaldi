from PyQt5.QtGui import QTextCursor, QTextDocument, QKeySequence
from PyQt5.QtWidgets import QAction
from extensions import actions

import app, cursortools
import icons
import tokeniter
from ly.lex import Token


def user_variable_at_cursor(cursor: QTextCursor) -> Token:
    from ly.lex.lilypond import ParseGlobal, Name

    cursortools.strip_selection(cursor)
    block = cursortools.block(cursor)
    state = tokeniter.state(block)
    partitions = tokeniter.partition(cursor)

    if isinstance(state.parser(), ParseGlobal) and isinstance(partitions.middle, Name):
        return partitions.middle


def get_cursor() -> QTextCursor:
    return app.activeWindow().textCursor()


def delete_line():
    cursor = get_cursor()
    # crs.select(QTextCursor.BlockUnderCursor)
    # crs.removeSelectedText()
    # crs.movePosition(QTextCursor.NextRow)

    start = end = cursortools.block(cursor)
    while end.position() + end.length() < cursor.selectionEnd():
        end = end.next()

    cursor.setPosition(start.position())
    cursor.setPosition(end.position(), cursor.KeepAnchor)
    cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
    cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor)
    cursor.removeSelectedText()


class Actions(actions.ExtensionActionCollection):

    def createActions(self, parent):
        """Create all actions that are available within this extension.
        Will be called automatically."""
        # Create actions
        self.generic_action = QAction(parent)
        # Icons can be loaded from the extension's `icons` subdirectory
        self.generic_action.setIcon(icons.get('twotone-calendar_view_day-24px'))
        from PyQt5.QtCore import Qt
        self.delete_current_line = QAction(parent)
        self.delete_current_line.setShortcutVisibleInContextMenu(True)
        self.delete_current_line.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Delete))

    # Implicitly called functions

    # This must be implemented
    def translateUI(self):
        self.generic_action.setText(_("Generic action (print message)"))
        self.generic_action.setToolTip(_("A longer text stored as multiline string"))

        self.delete_current_line.setText(_('Delete current line'))

    # The following functions *can* be implemented
    def configure_menu_actions(self):
        """Specify the behaviour of the menus."""

        # Show all actions in the Tools menu
        self.set_menu_action_list('tools', None)

        # Show specific action(s) in the editor context menu
        self.set_menu_action_list('editor', [self.generic_action, self.delete_current_line])

        # Show no actions (=> no submenu) in the music view context menu
        self.set_menu_action_list('musicview', [])

    def connect_actions(self):
        """Connect actions to their handlers."""
        self.generic_action.triggered.connect(self.generic_action_triggered)
        self.delete_current_line.triggered.connect(delete_line)

    def load_settings(self):
        """Load settings from settings file."""
        # Main use is to enable and disable actions
        self.generic_action.setEnabled(self.settings().get('show'))

    # Custom functionality

    def generic_action_triggered(self):
        import inputdialog

        crs = get_cursor()

        token = user_variable_at_cursor(crs)
        if token:
            name = inputdialog.getText(app.activeWindow(), title=_("Refactor"), message=_("Rename variable to:"),
                                       text='', regexp="[A-Za-z]+")
            rename_variable(token, name.strip())


def rename_variable(token: Token, new_name):
    from ly.document import Runner, Document
    from ly.lex.lilypond import UserCommand

    doc: QTextDocument = app.activeWindow().currentDocument()
    runner: Runner = Runner(Document(doc.toPlainText()))
    tk = runner.next()
    cursor: QTextCursor = QTextCursor(doc)

    while tk:
        if isinstance(tk, UserCommand):
            if tk[1:] == token[0:]:
                cursor.setPosition(tk.pos + 1)
                cursor.setPosition(tk.end, QTextCursor.KeepAnchor)
                cursor.insertText(new_name)
                print(type(tk))
            print(tk)

        tk = runner.next()
