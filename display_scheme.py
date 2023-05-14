from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QTextEdit, QTextBrowser, QVBoxLayout, QPushButton, QWidget, QDockWidget

import actioncollection
import app
import panel


class SchemeLogWidget(QWidget):
    def __init__(self, tool):
        super(SchemeLogWidget, self).__init__(tool)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 10, 0, 0)

        bt = QPushButton("Press")
        layout.addWidget(bt)
        layout.addWidget(QTextEdit())


class SchemeLog(panel.Panel):
    def __init__(self, mainWindow):
        super(SchemeLog, self).__init__(mainWindow)
        self.hide()
        self.setFloating(False)
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)

    def translateUI(self):
        self.setWindowTitle("Scheme Log")

    def createWidget(self):
        w = SchemeLogWidget(self)
        return w


def ggg():
    SchemeLog(app.activeWindow()).activate()
    pass


# noinspection PyPep8Naming
class ActionsCollection(actioncollection.ActionCollection):
    name = "display scheme"

    def createActions(self, parent=None):
        self.scheme_log = QAction(parent)
        self.scheme_log.triggered.connect(ggg)

    def translateUI(self):
        super().translateUI()
        self.scheme_log.setText("Scheme Log")


ac = ActionsCollection()
