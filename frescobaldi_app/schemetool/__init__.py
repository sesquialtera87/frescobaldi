import os

from PyQt5.QtCore import Qt, QProcess, QSize
from PyQt5.QtGui import QTextCursor, QTextDocument, QTextCharFormat, QBrush, QColor, QFont, QClipboard
from PyQt5.QtWidgets import QAction, QTextEdit, QVBoxLayout, QWidget, QToolBar, QApplication, QDockWidget

import actioncollection
import app
import panel

import ly.document

editor: QTextEdit = None


class SchemeLogWidget(QWidget):
    def __init__(self, tool):
        super(SchemeLogWidget, self).__init__(tool)
        import qtawesome as qta

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.copy_action = QAction(self)
        self.copy_action.setIcon(qta.icon('fa5s.copy'))
        self.copy_action.triggered.connect(to_clipboard)

        self.clear_action = QAction(self)
        self.clear_action.setIcon(qta.icon('fa5s.broom'))
        self.clear_action.triggered.connect(clear_log)

        lng = QAction(self)
        lng.setIcon(qta.icon('fa5s.hashtag'))
        lng.triggered.connect(find_language)

        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addActions([self.copy_action, self.clear_action, lng])

        self.setLayout(layout)

        global editor
        layout.addWidget(toolbar)
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setTabStopWidth(8)
        layout.addWidget(editor)


def find_language():
    from ly.document import Document, Runner
    import ly.lex.lilypond as llp

    window = app.activeWindow()
    doc: QTextDocument = window.currentDocument()
    document = Document(doc.toPlainText())
    runner = Runner(document)
    tk = runner.next()

    def find_token(cls, wait=False):
        """
        Find a token in the Runner belonging to the given class
        :param cls:
        :param wait:
        :return: The token or False if not found
        """
        tk = runner.next()

        if wait:
            while tk:
                if isinstance(tk, cls):
                    return True
                tk = runner.next()
        else:
            return tk and isinstance(tk, cls)
        return False

    language = None

    while tk:
        print(tk)
        if isinstance(tk, llp.Keyword) and tk.startswith('\\language'):
            if find_token(llp.StringQuotedStart, True):
                if find_token(llp.String):
                    language = runner.token()
                    print(language.upper())
                    if not find_token(llp.StringQuotedEnd):
                        language = None
                        break
                else:
                    break
        tk = runner.next()

    return language


def clear_log():
    editor.clear()


def to_clipboard():
    cb: QClipboard = QApplication.clipboard()
    cb.setText(editor.toPlainText()[_scheme[0]:_scheme[1]].strip())


class SchemeLog(panel.Panel):
    def __init__(self, mainWindow):
        super(SchemeLog, self).__init__(mainWindow)
        self.hide()
        self.setFloating(False)
        d: QDockWidget = self
        self.setContentsMargins(0, 5, 0, 0)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)

    def translateUI(self):
        self.setWindowTitle(_("Scheme Log"))

        # translate toolbar actions
        w = self.widget()
        w.copy_action.setToolTip(_('Copy Scheme code to the clipboard'))
        w.clear_action.setToolTip(_('Clear log'))

    def createWidget(self):
        w = SchemeLogWidget(self)
        return w


def show_log_widget() -> SchemeLog:
    import panelmanager
    pm = panelmanager.manager(app.activeWindow())
    panel = pm.panel_by_name('schemetool')
    panel.activate()
    return panel


_scheme = None


def lily_end(p: QProcess):
    c = cursor_for_last_block()
    editor.setTextCursor(c)

    if p.exitCode() == 1:
        frm = QTextCharFormat()
        frm.setForeground(QBrush(QColor('#f75464')))
        frm.setFontWeight(QFont.Bold)
        c.insertBlock()
        c.insertText('\nConversion failed', frm)
    elif p.exitCode() == 0:
        frm = QTextCharFormat()
        frm.setForeground(QBrush(QColor('#006400')))
        frm.setFontWeight(QFont.Normal)
        text = p.readAllStandardOutput().data().decode('utf-8')
        global _scheme
        _scheme = c.position(), len(text)
        c.insertBlock()
        c.insertText(text, frm)
    else:
        c.insertText('\n?????????????')


def cursor_for_last_block():
    doc: QTextDocument = editor.document()
    crs = QTextCursor(doc)
    crs.movePosition(QTextCursor.End)
    return crs


def insert_and_format_selection(selection: str):
    editor.clear()
    crs = cursor_for_last_block()
    frm = QTextCharFormat()
    frm.setForeground(QBrush(QColor('#808080')))
    frm.setFontWeight(QFont.Bold)
    crs.insertText('\\displayMusic ', frm)
    frm.setFontWeight(QFont.Normal)
    crs.insertText('{\n', frm)

    for line in selection.splitlines(keepends=True):
        crs.insertText('\t' + line.lstrip(), frm)

    crs.insertText('\n}')


def display_music():
    import documentinfo
    import lilypondinfo
    import util
    from string import Template

    show_log_widget()

    tmp = Template('\\version \"$version\"\n$lang {\n\\displayMusic{\n$selection\n}}')
    infos = lilypondinfo.infos()[0]
    window = app.activeWindow()
    cursor: QTextCursor = window.textCursor()
    document = cursor.document()
    language = find_language()
    language = f'\\language \"{language}\"\n' if language else ''
    selection = cursor.selection().toPlainText()
    installed_version = infos.versionString()
    doc_version = documentinfo.docinfo(document).version()

    insert_and_format_selection(selection)
    # if doc_version == ():
    #     version = installed_version
    # elif installed_version < doc_version:
    #     version = installed_version
    # else:
    #     version = doc_version
    # print(version)

    tmp = tmp.substitute(version=installed_version, selection=selection, lang=language)
    dir = util.tempdir()  # temporary folder
    filename = os.path.join(dir, 'document.ly')

    with open(filename, 'wb') as f:
        f.write(tmp.encode('utf-8'))

    p = QProcess()
    p.finished.connect(lambda: lily_end(p))
    p.errorOccurred.connect(lambda: lily_end(p))
    p.setProgram(infos.abscommand())
    p.setArguments([f"--output={dir}", filename])
    p.start()


# noinspection PyPep8Naming,PyUnresolvedReferences,PyAttributeOutsideInit
class ActionsCollection(actioncollection.ActionCollection):
    name = "display scheme"

    def createActions(self, parent=None):
        self.scheme_log = QAction(parent)
        self.scheme_log.triggered.connect(show_log_widget)
        self.display_music = QAction(parent)
        self.display_music.triggered.connect(display_music)

    def translateUI(self):
        self.scheme_log.setText(_("Scheme Log"))
        self.display_music.setText(_('Show Scheme for music'))


ac = ActionsCollection()
