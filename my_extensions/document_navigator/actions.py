from PyQt5.QtWidgets import QAction
from extensions import actions


class Actions(actions.ExtensionActionCollection):

    def createActions(self, parent):
        """Create all actions that are available within this extension.
        Will be called automatically."""
        # Create actions
        self.generic_action = QAction(parent)

    # This must be implemented
    def translateUI(self):
        self.generic_action.setText(_("Generic action (print message)"))
        self.generic_action.setToolTip(_("A longer text stored as multiline string"))

    def configure_menu_actions(self):
        """Specify the behaviour of the menus."""

        # Show all actions in the Tools menu
        self.set_menu_action_list('tools', None)

        # Show specific action(s) in the editor context menu
        self.set_menu_action_list('editor', [self.generic_action, ])

        # Show no actions (=> no submenu) in the music view context menu
        self.set_menu_action_list('musicview', [])

    def connect_actions(self):
        """Connect actions to their handlers."""
        self.generic_action.triggered.connect(self.generic_action_triggered)

    def load_settings(self):
        pass

    def generic_action_triggered(self):
        pass
