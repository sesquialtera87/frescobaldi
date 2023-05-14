from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction

import actioncollection
import panel
import app


# from frescobaldi_app.panel import Panel

class SchemeLog(panel.Panel):
    def __init__(self, mainWindow):
        super(SchemeLog, self).__init__(mainWindow)
        self.hide()
        mainWindow.addDockWidget(Qt.LeftDockWidgetArea, self)

    def translateUI(self):
        self.setWindowTitle("Scheme Log")

    def createWidget(self):
        import widget

        w = widget.Widget(self)
        return w


def ggg():
    SchemeLog(app.activeWindow()).activate()
    pass


class ActionsCollection(actioncollection.ActionCollection):
    name = "scheme"

    def createActions(self, parent=None):
        self.scheme_log = QAction(parent)
        self.scheme_log.triggered.connect(ggg)

    def translateUI(self):
        super().translateUI()
        self.scheme_log.setText("Scheme Log")


ac = ActionsCollection()
