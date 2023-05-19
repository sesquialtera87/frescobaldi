from PyQt5.QtCore import Qt
import extensions
from . import actions, config, widget


class Extension(extensions.Extension):
    """
    Boilerplate extension "My Extension".

    This is a minimal, working Frescobaldi extension providing
    stubs for all relevant functions.
    """

    # Extension configuration through class variables
    _action_collection_class = actions.Actions
    # _panel_widget_class = widget.Widget
    _panel_dock_area = Qt.LeftDockWidgetArea
    # _config_widget_class = config.Config
    _settings_config = {
        'show': True,
        'message': _("Initial extension message")
    }

    def __init__(self, parent, name):
        # __init__ is not necessarily needed, can be removed
        super(Extension, self).__init__(parent, name)

    def app_settings_changed(self):
        """Update extension status after global settings change."""
        # This is called automatically by the Extension base class
        pass

    def settings_changed(self, key, old, new):
        """Update extension status after extension settings change."""
        # this is triggered before app_settings_changed
        if key == 'show':
            self.action_collection().generic_action.setEnabled(new)
