import os

from PyQt5.QtCore import Qt, QProcess, QSize, QSettings
from PyQt5.QtGui import QTextCursor, QTextDocument, QTextCharFormat, QBrush, QColor, QFont, QClipboard
from PyQt5.QtWidgets import QAction, QTextEdit, QVBoxLayout, QWidget, QToolBar, QApplication, QDockWidget

import actioncollection
import app
import panel

import ly.document


class SchemeLogWidget(QWidget):
    def __init__(self, tool):
        super(SchemeLogWidget, self).__init__(tool)
        import qtawesome as qta

        self.job = None

        self.copy_action = QAction(self)
        self.copy_action.setIcon(qta.icon('fa5s.copy'))
        self.copy_action.triggered.connect(self.to_clipboard)

        self.clear_action = QAction(self)
        self.clear_action.setIcon(qta.icon('fa5s.broom'))
        self.clear_action.triggered.connect(self.clear_log)

        lng = QAction(self)
        lng.setIcon(qta.icon('fa5s.hashtag'))
        lng.triggered.connect(lambda: find_language(app.activeWindow().currentDocument()))

        toolbar = QToolBar()
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(24, 24))
        toolbar.addActions([self.copy_action, self.clear_action, lng])

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
        job.done.connect(lambda: self.lily_end)
        job.started.connect(lambda: print('start'))

    def clear_log(self):
        self.editor.clear()

    def to_clipboard(self):
        """ Copy last Scheme code to the clipboard """
        cb: QClipboard = app.qApp.clipboard()
        cb.setText(self.editor.toPlainText()[_scheme[0]:_scheme[1]].strip())

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

    def lily_end(self):
        print('end')
        c = self.cursor_for_last_block()
        self.editor.setTextCursor(c)

        if self.job.error is not None:
            frm = QTextCharFormat()
            frm.setForeground(QBrush(QColor('#f75464')))
            frm.setFontWeight(QFont.Bold)
            c.insertBlock()
            c.insertText('\nConversion failed', frm)
        else:
            frm = QTextCharFormat()
            frm.setForeground(QBrush(QColor('#006400')))
            frm.setFontWeight(QFont.Normal)
            text = self.job.stdout
            # text = p.readAllStandardOutput().data().decode('utf-8')
            global _scheme
            _scheme = c.position(), len(text)
            c.insertBlock()
            c.insertText(text, frm)


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
        import panelmanager
        pm = panelmanager.manager(app.activeWindow())
        return pm.panel_by_name(SchemeLog.NAME)


def show_log_widget():
    SchemeLog.instance().activate()


_scheme = None


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

    # p = QProcess()
    # p.finished.connect(lambda: lily_end(p))
    # p.errorOccurred.connect(lambda: lily_end(p))
    # p.setProgram(infos.abscommand())
    # p.setArguments([f"--output={dir}", filename])
    # p.start()


def run(file, dir):
    import lilypondinfo
    import job
    import sys
    infos = lilypondinfo.infos()[0]
    print(infos.abscommand())
    command = [infos.abscommand(), f"--output={dir}", file]
    command = ['\"' + infos.abscommand() + '\"', ]

    j = job.Job(command, encoding='utf-8')
    w: SchemeLogWidget = SchemeLog.instance().widget()
    w.set_job(j)

    if QSettings().value("lilypond_settings/no_translation", False, bool):
        j.environment['LC_MESSAGES'] = 'C'
    else:
        j.environment.pop('LC_MESSAGES', None)

    if sys.platform.startswith('darwin'):
        import macosx
        if macosx.inside_app_bundle():
            j.environment['PYTHONPATH'] = None
            j.environment['PYTHONHOME'] = None

    app.job_queue().add_job(j, 'generic')


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
                    language = runner.token()

                    if not find_token(llp.StringQuotedEnd):
                        language = None
                        break
                    else:
                        break
                else:
                    break
        tk = runner.next()

    return language


ac = ActionsCollection()
