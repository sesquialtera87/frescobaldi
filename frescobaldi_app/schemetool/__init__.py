import os

from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QTextCursor, QTextDocument, QTextCharFormat, QBrush, QColor, QFont
from PyQt5.QtWidgets import QAction, QTextEdit, QVBoxLayout, QPushButton, QWidget

import actioncollection
import app
import panel

editor: QTextEdit = None


class SchemeLogWidget(QWidget):
    def __init__(self, tool):
        super(SchemeLogWidget, self).__init__(tool)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 10, 0, 0)

        bt = QPushButton("Press")

        global editor
        layout.addWidget(bt)
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setTabStopWidth(8)
        layout.addWidget(editor)


class SchemeLog(panel.Panel):
    def __init__(self, mainWindow):
        super(SchemeLog, self).__init__(mainWindow)
        self.hide()
        self.setFloating(False)
        from PyQt5.QtWidgets import QDockWidget
        import qtawesome as qta
        d: QDockWidget = self
        self.setWindowIcon(qta.icon('fa5s.hashtag', color='black'))
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)

    def translateUI(self):
        self.setWindowTitle("Scheme Log")

    def createWidget(self):
        w = SchemeLogWidget(self)
        return w


def show_log_widget():
    import panelmanager
    pm = panelmanager.manager(app.activeWindow())
    panel = pm.panel_by_name('schemetool')
    panel.activate()


def lily_end(p: QProcess):
    c = cursor_for_last_block()
    editor.setTextCursor(c)

    if p.exitCode() == 1:
        frm = QTextCharFormat()
        frm.setForeground(QBrush(QColor('#f75464')))
        frm.setFontWeight(QFont.Bold)
        c.insertText('\nConversion failed', frm)
    elif p.exitCode() == 0:
        frm = QTextCharFormat()
        frm.setForeground(QBrush(QColor('#006400')))
        frm.setFontWeight(QFont.Normal)
        c.insertText('\n')
        text = p.readAllStandardOutput().data().decode('utf-8')
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

    crs.insertText('\n}\n')


def display_music():
    import documentinfo
    import lilypondinfo
    import util
    from string import Template

    show_log_widget()

    tmp = Template('\\version \"$version\"\n {\n\\displayMusic{\n$selection\n}}')
    infos = lilypondinfo.infos()[0]
    window = app.activeWindow()
    cursor: QTextCursor = window.textCursor()
    document = cursor.document()
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

    tmp = tmp.substitute(version=installed_version, selection=selection)
    dir = util.tempdir()
    filename = os.path.join(dir, 'document.ly')
    print(filename)

    with open(filename, 'wb') as f:
        f.write(tmp.encode('utf-8'))

    p = QProcess()
    p.finished.connect(lambda: lily_end(p))
    p.errorOccurred.connect(lambda: lily_end(p))
    p.setProgram(infos.abscommand())
    p.setArguments([f"--output={dir}", filename])
    p.start()


# noinspection PyPep8Naming
class ActionsCollection(actioncollection.ActionCollection):
    name = "display scheme"

    def createActions(self, parent=None):
        self.scheme_log = QAction(parent)
        self.scheme_log.triggered.connect(show_log_widget)
        self.display_music = QAction(parent)
        self.display_music.triggered.connect(display_music)

    def translateUI(self):
        super().translateUI()
        self.scheme_log.setText(_("Scheme Log"))
        self.display_music.setText(_('Show Scheme for music'))


ac = ActionsCollection()
