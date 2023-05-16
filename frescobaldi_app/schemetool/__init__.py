import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QTextCursor, QTextDocument, QTextCharFormat, QBrush, QColor, QFont, QClipboard
from PyQt5.QtWidgets import QAction, QTextEdit, QVBoxLayout, QWidget, QToolBar

import actioncollection
import app
import job
import panel
import panelmanager


class SchemeLogWidget(QWidget):
    def __init__(self, tool):
        super(SchemeLogWidget, self).__init__(tool)
        import qtawesome as qta

        self.job = None
        self.scheme_code = None

        self.copy_action = QAction(self)
        self.copy_action.setIcon(qta.icon('fa5s.copy'))
        self.copy_action.triggered.connect(self.to_clipboard)

        self.clear_action = QAction(self)
        self.clear_action.setIcon(qta.icon('fa5s.broom'))
        self.clear_action.triggered.connect(self.clear_log)

        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addActions([self.copy_action, self.clear_action])

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setTabStopWidth(8)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(toolbar)
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def set_job(self, job):
        self.job = job
        self.scheme_code = None

        job.output.connect(self.write_output)

    def write_output(self, message, tp):
        if self.scheme_code is None and tp == job.STDOUT:
            if message.lstrip().startswith('('):
                self.scheme_code = message
        elif tp == job.SUCCESS:
            frm = QTextCharFormat()
            frm.setForeground(QBrush(QColor('#006400')))
            frm.setFontWeight(QFont.Normal)

            crs = self.editor.textCursor()
            crs.movePosition(QTextCursor.End)
            crs.insertBlock()
            crs.insertText(self.scheme_code, frm)

            self.job.output.disconnect(self.write_output)
        elif tp == job.FAILURE:
            frm = QTextCharFormat()
            frm.setForeground(QBrush(QColor('#f75464')))
            frm.setFontWeight(QFont.Bold)

            crs = self.editor.textCursor()
            crs.movePosition(QTextCursor.End)
            crs.insertBlock()
            crs.insertText('Conversion failed', frm)

            self.job.output.disconnect(self.write_output)

    def clear_log(self):
        self.editor.clear()

    def to_clipboard(self):
        """ Copy last Scheme code to the clipboard """
        cb: QClipboard = app.qApp.clipboard()
        cb.setText(self.scheme_code)

    def cursor_for_last_block(self):
        doc: QTextDocument = self.editor.document()
        crs = QTextCursor(doc)
        crs.movePosition(QTextCursor.End)
        return crs

    def insert_and_format_selection(self, selection: str):
        self.editor.clear()
        crs = self.cursor_for_last_block()
        frm = QTextCharFormat()
        frm.setForeground(QBrush(QColor('#808080')))
        frm.setFontWeight(QFont.Bold)
        crs.insertText('\\displayMusic ', frm)
        frm.setFontWeight(QFont.Normal)
        crs.insertText('{\n', frm)

        for line in selection.splitlines(keepends=True):
            crs.insertText('\t' + line.lstrip(), frm)

        crs.insertText('\n}')


class SchemeLog(panel.Panel):
    NAME = 'schemetool'

    def __init__(self, mainWindow):
        super(SchemeLog, self).__init__(mainWindow)
        self.hide()
        self.setFloating(False)
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

    @staticmethod
    def instance() -> panel.Panel:
        pm = panelmanager.manager(app.activeWindow())
        return pm.panel_by_name(SchemeLog.NAME)


def show_log_widget():
    SchemeLog.instance().activate()


def display_music():
    import documentinfo
    import lilypondinfo
    import util
    from string import Template

    show_log_widget()

    tmp = Template('\\version \"$version\"\n$lang {\n\\displayMusic{\n$selection\n}}')
    infos = lilypondinfo.infos()[0]
    cursor: QTextCursor = app.activeWindow().textCursor()
    document: QTextDocument = cursor.document()
    language = find_language(document)
    language = f'\\language \"{language}\"\n' if language else ''
    selection = cursor.selection().toPlainText()
    installed_version = infos.versionString()
    doc_version = documentinfo.docinfo(document).version()

    SchemeLog.instance().widget().insert_and_format_selection(selection)
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

    run(filename, dir)


def run(file, folder):
    import lilypondinfo
    info = lilypondinfo.infos()[0]
    command = [info.abscommand(), f'--output={folder}', file]

    j = job.Job(command, encoding='utf-8')
    w: SchemeLogWidget = SchemeLog.instance().widget()
    w.set_job(j)

    jm = job.manager.manager(app.activeWindow().currentDocument())
    jm.start_job(j)


# noinspection PyPep8Naming,PyUnresolvedReferences,PyAttributeOutsideInit
class ActionsCollection(actioncollection.ActionCollection):
    name = 'display scheme'

    def createActions(self, parent=None):
        self.scheme_log = QAction(parent)
        self.scheme_log.triggered.connect(show_log_widget)
        self.display_music = QAction(parent)
        self.display_music.triggered.connect(display_music)

    def translateUI(self):
        self.scheme_log.setText(_('Scheme Log'))
        self.display_music.setText(_('Show Scheme for music'))


def find_language(doc: QTextDocument) -> str:
    """ Search the language specification in the document """
    from ly.document import Document, Runner
    import ly.lex.lilypond as llp

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
        if isinstance(tk, llp.Keyword) and tk.startswith('\\language'):
            if find_token(llp.StringQuotedStart, True):
                if find_token(llp.String):
                    language = runner.token()  # read string value

                    if not find_token(llp.StringQuotedEnd):
                        language = None
                    break
                else:
                    break
        tk = runner.next()

    return language


ac = ActionsCollection()
