
import time
import threading

import ipywidgets
import IPython

from . import api
from . import commands
from .namespace import Struct

from .monotext_widget import MonoText
from .task import Task



class MetadataTask(Task):
    """Task subclass for managing camera metadata
    """
    _raw_settings = None
    _raw_status = None
    _info_status = None
    _time_stamp = 0
    _data_callback = None

    def __init__(self, data_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_callback = data_callback

    def initialize(self):
        super().initialize()

        # Fetch some fresh camera data right now
        raw_status_settings = commands.get_raw_status_settings()
        self._update_data(raw_status_settings)

    @property
    def stale(self):
        """True if currently-stored data is stale
        """
        return self._time_stamp + self.interval < time.time()

    @property
    def have_data(self):
        """Return True if internal data is available
        """
        if self._raw_settings and self._raw_status and self._info_status:
            return True
        else:
            return False

    def _update_data(self, raw_status_settings):
        """Perform the work of updating internal data
        """
        raw_status, raw_settings = raw_status_settings

        if not raw_status:
            self._raw_status = None
            self._raw_settings = None
            self._info_status = None

            return
            # raise ValueError('Unexpected value for raw_status: {}'.format(raw_status))

        # Share raw data with peers?
        if self._data_callback:
            self._data_callback(raw_status_settings)

        # Process status subset
        info_status_full = api.parse_status_names(raw_status)

        info_status = Struct()
        for k in api._status_fields:
            info_status[k] = info_status_full[k]

        # Pretty mode/sub-mode names instead of integers
        name_mode, name_sub_mode = api.parse_mode_sub_mode(info_status)
        info_status.mode = name_mode
        info_status.sub_mode = name_sub_mode

        # Incorporate new metadata
        self._raw_settings = raw_settings
        self._raw_status = raw_status
        self._info_status = info_status

        self._time_stamp = time.time()


    def update(self, raw_status_settings=None, force=False, **kwargs):
        """Update internal state information
        """
        super().update(**kwargs)

        if not raw_status_settings and not self.stale and not force:
            # No new data, old data still fresh
            return

        # Fetch new camera information, update self
        if not raw_status_settings:
            raw_status_settings = commands.get_raw_status_settings()
        self._update_data(raw_status_settings)

    def finish(self):
        """Clear out the data, prepare to shut down.
        """
        super().finish()

        self._raw_status = None
        self._raw_settings = None
        self._info_status = None

#------------------------------------------------


class Status(MetadataTask):
    """Monitor camera status
    """
    _widget = None

    def __init__(self, auto_start=True, auto_display=True, *args, **kwargs):
        super().__init__(auto_start=auto_start, *args, **kwargs)
        self._auto_display = auto_display

    def initialize(self):
        super().initialize()

        self._widget = MonoText()
        self._widget.text = 'waiting for data...'
        if self._auto_display:
            self.display()

    def display(self):
        if self._widget:
            IPython.display.display(self._widget)

    def update(self, raw_status_settings=None, **kwargs):
        """Update internal data and displayed widgets
        """
        super().update(raw_status_settings=raw_status_settings, **kwargs)
        self._update_widget()

    def _update_widget(self):
        """Update display widget with new text information
        """
        if self.have_data:
            # Maximum label width
            L = 0
            for k in self._info_status.keys():
                if len(k) > L:
                    L = len(k)

            # Assemble formatted lines of text
            tpl = '{{:{L:d}s}}: {{}}'.format(L=L+1)
            lines_of_text = []
            for k, v in self._info_status.items():
                lines_of_text.append(tpl.format(k, v))

            # Push text to the widget
            self._widget.text = lines_of_text
        else:
            if 'still' in self._widget.text:
                self._widget.text = 'waiting for data...'
            else:
                self._widget.text = '...still waiting for data'

    def finish(self):
        """Shut down the widgets
        """
        super().finish()

        if self._widget:
            self._widget.close()
            self._widget = None


#################################################


def feature_dropdown_widget(mode, f_name, width='160pt', callback=None):
    """Construct a dropdown widget for specified feature options.
    Attach event handler to deliver new values to camera.
    Embed optional callback function to be called for each event.
    """
    f_name, fid, options = api.feature_options(mode, f_name)
    options_data = [(x['display_name'], x['value']) for x in options]

    # Instantiate new dropdown widget
    d_name = api.feature_display_name(mode, f_name)
    wid = ipywidgets.Dropdown(options=options_data, description=d_name)
    wid.layout.width = width

    # Define event handler
    def _handle_selection(event):
        if event.type == 'change':
            value = event.new

            resp = commands.set_feature_value(fid, value)

            if resp.ok and callback:
                callback()

            if not resp.ok:
                # raise exception instead??
                print(resp.status_code)


    # Attach event handler to widget
    wid.observe(_handle_selection, names='value')

    return wid



class Settings(MetadataTask):
    """Manage camera settings
    """
    _widgets = None
    _wid_box = None
    _mode = None

    def __init__(self, auto_start=True, auto_display=True, *args, **kwargs):
        super().__init__(auto_start=auto_start, *args, **kwargs)
        self._auto_display = auto_display

    def initialize(self):
        super().initialize()

        self._update_mode()
        self._generate_widgets()

        if self._auto_display:
            self.display()

    def display(self):
        if self._wid_box:
            IPython.display.display(self._wid_box)

    def update(self, raw_status_settings=None, **kwargs):
        """Update internal data and displayed widgets
        """
        super().update(raw_status_settings=raw_status_settings, **kwargs)
        changed = self._update_mode()
        if changed:
            self._generate_widgets()
        self._update_widgets()

    def callback_update(self):
        raw_status_settings = commands.get_raw_status_settings()
        self.update(raw_status_settings)

    def _update_mode(self):
        """Update camera mode, return True if mode has changed
        """
        new_mode = self._info_status.mode

        if new_mode not in api.features:
            raise ValueError('Unexpected mode value: {}'.format(new_mode))

        if new_mode != self._mode:
            self._mode = new_mode
            changed = True
            # self._generate_widgets()
            # self._update_widgets()
        else:
            changed = False

        return changed

    def _generate_widgets(self):
        """Generate/regenerate dropdown widgets to control camera mode options
        """
        self._close_widgets()  # dropdown widgets only, not the container box widget

        # Vertical layout box to contain the dropdown widgets
        if not self._wid_box:
            self._wid_box = ipywidgets.VBox()

        # Make new widgets
        self._widgets = Struct()
        for f_name in api.features[self._mode]:
            wid = feature_dropdown_widget(self._mode, f_name, callback=self.callback_update)

            self._widgets[f_name] = wid

        self._wid_box.children = [wid for wid in self._widgets.values()]

    def _update_widgets(self):
        """Update displayed widgets with current camera settings
        """
        if self._widgets:
            for f_name, wid in self._widgets.items():
                fid = api.feature_name_id(self._mode, f_name)
                value_new = self._raw_settings[fid]
                if wid.value != value_new:
                    wid.value = value_new

    def _close_widgets(self):
        """Close dropdown widgets inside container box widget
        """
        if self._widgets:
            for wid in self._widgets.values():
                wid.close()
            self._widgets = None

        if self._wid_box:
            self._wid_box.children = []

    def finish(self):
        """Close and remove all widgets
        """
        self._close_widgets()

        if self._wid_box:
            self._wid_box.close()
            self._wid_box = None



class GoPro():
    """Simple container
    """
    _widget = None

    def __init__(self):

        self._settings = Settings(auto_start=True, auto_display=False, interval=10)
        self._status = Status(auto_start=True, auto_display=False, interval=2)

        while self._status._widget is None:
            time.sleep(0.01)

        while self._settings._wid_box is None:
            time.sleep(0.01)


        self._widget = ipywidgets.HBox([self._settings._wid_box, self._status._widget])

        self.display()

    @property
    def status(self):
        return self._status._info_status

    def update(self):
        self._status.update(force=True)

    def display(self):
        if self._widget:
            IPython.display.display(self._widget)

    def stop(self):
        self._status.stop()
        self._settings.stop()

#------------------------------------------------

if __name__ == '__main__':
    pass

