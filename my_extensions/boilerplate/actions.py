# This file is part of the Frescobaldi Extensions project,
# https://github.com/frescobaldi-extensions
#
# Copyright (c) 2018 by Urs Liska and others
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
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

# Boilerplate Extension - Action collection

from PyQt5.QtWidgets import QAction
from extensions import actions
import icons, cursortools, tokeniter


class Actions(actions.ExtensionActionCollection):

    def createActions(self, parent):
        """Create all actions that are available within this extension.
        Will be called automatically."""
        # Create actions
        self.generic_action = QAction(parent)
        # Icons can be loaded from the extension's `icons` subdirectory
        self.generic_action.setIcon(icons.get('twotone-calendar_view_day-24px'))

    # Implicitly called functions

    # This must be implemented
    def translateUI(self):
        self.generic_action.setText(_("Generic action (print message)"))
        self.generic_action.setToolTip(_("A longer text stored as multiline string"))

    # The following functions *can* be implemented
    def configure_menu_actions(self):
        """Specify the behaviour of the menus."""

        # Show all actions in the Tools menu
        self.set_menu_action_list('tools', None)

        # Show specific action(s) in the editor context menu
        self.set_menu_action_list('editor', [self.generic_action])

        # Show no actions (=> no submenu) in the music view context menu
        self.set_menu_action_list('musicview', [])

    def connect_actions(self):
        """Connect actions to their handlers."""
        self.generic_action.triggered.connect(self.generic_action_triggered)

    def load_settings(self):
        """Load settings from settings file."""
        # Main use is to enable and disable actions
        self.generic_action.setEnabled(self.settings().get('show'))

    # Custom functionality

    def generic_action_triggered(self):
        import app, inputdialog
        from ly.lex.lilypond import ParseGlobal, Name

        cursor = app.activeWindow().textCursor()
        cursortools.strip_selection(cursor)
        block = cursortools.block(cursor)
        state = tokeniter.state(block)
        partitions = tokeniter.partition(cursor)

        if state.parser() and isinstance(partitions.middle, Name):
            name = inputdialog.getText(None, _("Cut and Assign"), _(
                "Please enter the name for the variable to assign the selected "
                "text to:"), regexp="[A-Za-z]+")
            if not name:
                return