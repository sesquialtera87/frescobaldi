import os
from hashlib import md5

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import (QGridLayout, QCheckBox, QLabel, QComboBox, QLineEdit, QWidget,
                             QHBoxLayout, QVBoxLayout, QPushButton, QGroupBox, QFileDialog, QDialog, QDialogButtonBox,
                             QMessageBox)
import app

_temp_settings_path = None


def show_export_dialog():
    dialog = HtmlDialog()
    dialog.exec_()


# noinspection PyUnresolvedReferences
def export_colored_html(filename):
    from highlight2html import html_document

    doc = app.activeWindow().currentDocument()
    s = QSettings()
    s.beginGroup("source_export")
    number_lines = s.value("number_lines", False, bool)
    inline_style = s.value("inline_export", False, bool)
    wrap_tag = s.value("wrap_tag", "pre", str)
    wrap_attrib = s.value("wrap_attrib", "id", str)
    wrap_attrib_name = s.value("wrap_attrib_name", "document", str)
    html = html_document(doc, inline=inline_style, number_lines=number_lines,
                         wrap_tag=wrap_tag, wrap_attrib=wrap_attrib,
                         wrap_attrib_name=wrap_attrib_name)
    try:
        with open(filename, "wb") as f:
            f.write(html.encode('utf-8'))
    except IOError as e:
        msg = _("{message}\n\n{strerror} ({errno})").format(
            message=_("Could not write to: {url}").format(url=filename),
            strerror=e.strerror,
            errno=e.errno)
        QMessageBox.critical(app.activeWindow(), app.caption(_("Error")), msg)


# noinspection PyArgumentList,PyUnresolvedReferences
class HtmlDialog(QDialog):

    def __init__(self):
        super().__init__(parent=app.activeWindow(), flags=Qt.Dialog)

        self.wrapAttribName = None
        self.wrapAttribNameLabel = None
        self.wrapperAttribute = None
        self.wrapAttribSelector = None
        self.wrapTagSelector = None
        self.wrapperTag = None
        self.numberLines = None
        self.inlineStyleCopy = None
        self.inlineStyleExport = None
        self.copyDocumentBodyOnly = None
        self.copyHtmlAsPlainText = None
        self.htmlFileNameTextField = None
        self.htmlDirTextField = None

        wdg = QWidget()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        layout_builders = [self.path_section, self.copy_section, self.style_section, self.html_structure_section]
        section_names = ['Path', 'Copy Options', 'Style', 'HTML Structure']
        for layout, name in zip(layout_builders, section_names):
            section = QGroupBox()
            section.setParent(wdg)
            section.setTitle(name)
            section.setCheckable(False)
            section.setLayout(layout())
            main_layout.addWidget(section, alignment=Qt.AlignTop)

        self.export_button = QPushButton('Export to HTML')
        self.export_button.clicked.connect(self.export)

        buttons = QDialogButtonBox()
        buttons.addButton(self.export_button, QDialogButtonBox.AcceptRole)
        buttons.setStandardButtons(QDialogButtonBox.Cancel)
        buttons.rejected.connect(lambda: self.reject())

        main_layout.addWidget(buttons)

        self.translate_ui()

    def _choose_directory(self):
        directory = self.htmlDirTextField.text().strip()

        if not directory or not os.path.exists(directory):
            directory = os.path.expanduser('~')

        dir = QFileDialog.getExistingDirectory(self.parent(),
                                               app.caption(("Choose directory")),
                                               directory,
                                               options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dir:
            self.htmlDirTextField.setText(dir)
            self.htmlFileNameTextField.setFocus()
            self.htmlFileNameTextField.selectAll()

    def _validate(self):
        directory = self.htmlDirTextField.text().strip()
        file_name = self.htmlFileNameTextField.text().strip()
        self.export_button.setEnabled(os.path.exists(directory) and len(file_name) != 0)

    def path_section(self):
        html_dir = QLabel('Directory:')
        html_name = QLabel('File name:')

        self.htmlDirTextField = QLineEdit()
        self.htmlDirTextField.textChanged.connect(self._validate)

        self.htmlFileNameTextField = QLineEdit()
        self.htmlFileNameTextField.textChanged.connect(self._validate)

        browse_button = QPushButton('...')
        browse_button.setMaximumWidth(40)
        browse_button.clicked.connect(self._choose_directory)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(html_dir)
        dir_layout.addWidget(self.htmlDirTextField)
        dir_layout.addWidget(browse_button)

        name_layout = QHBoxLayout()
        name_layout.addWidget(html_name)
        name_layout.addWidget(self.htmlFileNameTextField)

        layout = QGridLayout()
        layout.setSpacing(-1)

        layout.addWidget(html_dir, 0, 0, 1, 1)
        layout.addWidget(self.htmlDirTextField, 0, 1, 1, 1)
        layout.addWidget(browse_button, 0, 2, 1, 1)
        layout.addWidget(html_name, 1, 0, 1, 1)
        layout.addWidget(self.htmlFileNameTextField, 1, 1, 1, 1)

        return layout

    def copy_section(self):
        self.copyHtmlAsPlainText = QCheckBox()
        self.copyDocumentBodyOnly = QCheckBox()

        layout = QGridLayout()
        layout.addWidget(self.copyHtmlAsPlainText, 0, 0)
        layout.addWidget(self.copyDocumentBodyOnly, 0, 1)

        return layout

    def style_section(self):
        self.inlineStyleExport = QCheckBox()
        self.inlineStyleCopy = QCheckBox()

        layout = QGridLayout()
        layout.addWidget(self.inlineStyleExport, 0, 0)
        layout.addWidget(self.inlineStyleCopy, 0, 1)

        return layout

    def html_structure_section(self):
        self.numberLines = QCheckBox()
        self.wrapperTag = QLabel()
        self.wrapTagSelector = QComboBox()
        self.wrapperAttribute = QLabel()
        self.wrapAttribSelector = QComboBox()
        self.wrapAttribNameLabel = QLabel()
        self.wrapAttribName = QLineEdit()
        self.wrapperTag.setBuddy(self.wrapTagSelector)
        self.wrapperAttribute.setBuddy(self.wrapAttribSelector)
        self.wrapAttribNameLabel.setBuddy(self.wrapAttribName)

        self.wrapTagSelector.addItem("pre")
        self.wrapTagSelector.addItem("code")
        self.wrapTagSelector.addItem("div")
        self.wrapAttribSelector.addItem("id")
        self.wrapAttribSelector.addItem("class")

        layout = QGridLayout()
        layout.setSpacing(3)
        layout.addWidget(self.numberLines, 0, 0)
        layout.addWidget(self.wrapperTag, 1, 0)
        layout.addWidget(self.wrapTagSelector, 1, 1)
        layout.addWidget(self.wrapperAttribute, 2, 0)
        layout.addWidget(self.wrapAttribSelector, 2, 1)
        layout.addWidget(self.wrapAttribNameLabel, 3, 0)
        layout.addWidget(self.wrapAttribName, 3, 1)

        return layout

    def file_name(self):
        name = self.htmlFileNameTextField.text().strip()

        if not name.lower().endswith('.html'):
            name = name + '.html'

        # check override existing file??
        return os.path.join(self.htmlDirTextField.text().strip(), name)

    def exec_(self):
        self.load_settings()
        return super().exec_()

    def export(self):
        self.save_settings()
        self.accept()
        export_colored_html(self.file_name())

    def init(self):
        wdg: QWidget = QWidget()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        for section in [self.path_section, self.copy_section, self.style_section, self.html_structure_section]:
            main_layout.addWidget(section(wdg), Qt.AlignTop)

        self.export_button = QPushButton('Export to HTML')
        self.export_button.clicked.connect(self.export)

        buttons = QDialogButtonBox()
        buttons.addButton(self.export_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(QDialogButtonBox.Cancel)

        main_layout.addWidget(buttons)
        self.translateUI()

    @staticmethod
    def temp_settings() -> QSettings:
        global _temp_settings_path
        if not _temp_settings_path:
            import util
            _temp_settings_path = os.path.join(util.tempdir(), 'recents.ini')
        return QSettings(_temp_settings_path, QSettings.IniFormat)

    def load_settings(self):
        s = QSettings()
        s.beginGroup("source_export")

        tag_selector = self.wrapTagSelector.findText(s.value("wrap_tag", "pre", str), flags=Qt.MatchExactly)
        attrib_selector = self.wrapAttribSelector.findText(s.value("wrap_attrib", "id", str), flags=Qt.MatchExactly)

        self.numberLines.setChecked(s.value("number_lines", False, bool))
        self.inlineStyleCopy.setChecked(s.value("inline_copy", True, bool))
        self.inlineStyleExport.setChecked(s.value("inline_export", False, bool))
        self.copyHtmlAsPlainText.setChecked(s.value("copy_html_as_plain_text", False, bool))
        self.copyDocumentBodyOnly.setChecked(s.value("copy_document_body_only", False, bool))
        self.wrapTagSelector.setCurrentIndex(tag_selector)
        self.wrapAttribSelector.setCurrentIndex(attrib_selector)
        self.wrapAttribName.setText(s.value("wrap_attrib_name", "document", str))

        s = HtmlDialog.temp_settings()
        doc = app.activeWindow().currentDocument()
        path = doc.url().path()
        ck = md5(path.encode()).hexdigest()

        if ck in s.childGroups():
            s.beginGroup(ck)
            self.htmlDirTextField.setText(s.value('dir', '', str))
            self.htmlFileNameTextField.setText(s.value('filename', '', str))
            s.endGroup()
        else:
            if path:
                name, ext = os.path.splitext(os.path.basename(path))
                self.htmlDirTextField.setText(os.path.dirname(path).replace('/', '', 1))
                self.htmlFileNameTextField.setText(name + '.html')
            else:
                self.htmlDirTextField.setText(os.path.expanduser('~'))

        self.htmlFileNameTextField.setFocus()
        self.htmlFileNameTextField.selectAll()

    def save_settings(self):
        s = QSettings()
        s.beginGroup("source_export")
        s.setValue("number_lines", self.numberLines.isChecked())
        s.setValue("inline_copy", self.inlineStyleCopy.isChecked())
        s.setValue("inline_export", self.inlineStyleExport.isChecked())
        s.setValue("copy_html_as_plain_text", self.copyHtmlAsPlainText.isChecked())
        s.setValue("copy_document_body_only", self.copyDocumentBodyOnly.isChecked())
        s.setValue("wrap_tag", self.wrapTagSelector.currentText())
        s.setValue("wrap_attrib", self.wrapAttribSelector.currentText())
        s.setValue("wrap_attrib_name", self.wrapAttribName.text())

        doc_path = app.activeWindow().currentDocument().url().path()
        ck = md5(doc_path.encode()).hexdigest()

        s = HtmlDialog.temp_settings()
        s.beginGroup(ck)
        s.setValue('dir', self.htmlDirTextField.text().strip())
        s.setValue('filename', self.htmlFileNameTextField.text().strip())
        s.endGroup()

    def translate_ui(self):
        self.setWindowTitle(_("Export to HTML"))
        self.numberLines.setText(_("Show line numbers"))
        self.numberLines.setToolTip('<qt>' + _(
            "If enabled, line numbers are shown in exported HTML or printed "
            "source."))
        self.inlineStyleCopy.setText(_("Use inline style when copying colored HTML"))
        self.inlineStyleCopy.setToolTip('<qt>' + _(
            "If enabled, inline style attributes are used when copying "
            "colored HTML to the clipboard. "
            "Otherwise, a CSS stylesheet is embedded."))

        self.inlineStyleExport.setText(_("Use inline style when exporting colored HTML"))
        self.inlineStyleExport.setToolTip('<qt>' + _(
            "If enabled, inline style attributes are used when exporting "
            "colored HTML to a file. "
            "Otherwise, a CSS stylesheet is embedded."))
        self.copyHtmlAsPlainText.setText(_("Copy HTML as plain text"))
        self.copyHtmlAsPlainText.setToolTip('<qt>' + _(
            "If enabled, HTML is copied to the clipboard as plain text. "
            "Use this when you want to type HTML formatted code in a "
            "plain text editing environment."))
        self.copyDocumentBodyOnly.setText(_("Copy document body only"))
        self.copyDocumentBodyOnly.setToolTip('<qt>' + _(
            "If enabled, only the HTML contents, wrapped in a single tag, will be "
            "copied to the clipboard instead of a full HTML document with a "
            "header section. "
            "May be used in conjunction with the plain text option, with the "
            "inline style option turned off, to copy highlighted code in a "
            "text editor when an external style sheet is already available."))
        self.wrapperTag.setText(_("Tag to wrap around source:" + "  "))
        self.wrapperTag.setToolTip('<qt>' + _(
            "Choose what tag the colored HTML will be wrapped into."))
        self.wrapperAttribute.setText(_("Attribute type of wrapper:" + "  "))
        self.wrapperAttribute.setToolTip('<qt>' + _(
            "Choose whether the wrapper tag should be of type 'id' or 'class'"))
        self.wrapAttribNameLabel.setText(_("Name of attribute:" + "  "))
        self.wrapAttribNameLabel.setToolTip('<qt>' + _(
            "Arbitrary name for the type attribute. " +
            "This must match the CSS stylesheet if using external CSS."))
