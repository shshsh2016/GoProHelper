
import time
import threading

import ipywidgets
import IPython

from . import api
from . import commands
from .namespace import Struct

from .monotext_widget import MonoText
from .task import Task


class Status(Task):
    """Monitor camera status
    """
    def __init__(self, interval=1, auto_start=False):
        self._widget = None
        self._status = None
        self._time_stamp = 0

        super().__init__(interval=interval, auto_start=auto_start)

    def initialize(self):
        self._widget = MonoText()
        IPython.display.display(self._widget)
        self._widget.text = 'waiting for data...'

    def _update_data(self, status=None):
        """Update internal state information, being aware that external entities may have
        already provided fresh data.
        """
        time_now = time.time()

        if not status and (time_now > self._time_stamp + self.interval or not self._status):
            # Fetch new camera information
            status = commands.get_status()

        if status:
            name_mode, name_sub_mode = commands.parse_mode_submode(status)
            status.mode = name_mode
            status.sub_mode = name_sub_mode

            self._time_stamp = time_now
            self._status = status

    def _update_display(self):
        """Update display widget with new text information
        """
        if self._status:
            # Maximum label width
            L = 0
            for k in self._status.keys():
                if len(k) > L:
                    L = len(k)

            # Assemble formatted lines of text
            template = '{{:{L:d}s}}: {{}}'.format(L=L+1)
            lines_of_text = []
            for k, v in self._status.items():
                lines_of_text.append(template.format(k, v))

            self._widget.text = lines_of_text
        else:
            self._widget.text = 'still waiting for data...'

    def update(self):
        """Update internal data and the widget display
        """
        self._update_data()
        self._update_display()

    def external_update(self, status):
        if self._widget:
            with self.lock:
                self._update_data(status=status)
                self._update_display()

    def finish(self):
        if self._widget:
            self._widget.close()
            self._widget = None


#################################################

value_none = -1

def feature_dropdown_widget(mode, fid, name=None, value_init=value_none,
                            width='150pt', callback=None):
    """Construct a dropdown widget for specified feature options.
    Attach event handler to send new values to camera.
    Embed optional callback function to be called for each event.
    """
    _name, options = api.feature_choices(mode, fid, include_empty=True)

    if not name:
        name = _name

    # Instantiate new dropdown widget
    wid = ipywidgets.Dropdown(value=value_init, options=options, description=name)
    wid.layout.width = width

    # Define event handler
    def handle_selection(event):
        value = event.new
        if value != value_none:
            resp = commands.set_feature_value(fid, value)
            if not resp.ok:
                print(resp.status_code)

        if callback:
            callback()

    # Attach event handler to widget
    wid.observe(handle_selection, names='value')

    return wid



class Settings(Task):
    """Monitor and manage camera settings
    """
    def __init__(self, auto_start=False, interval=1):
        self.interval = interval
        self._thread = None
        self._flag_run = False
        self._mode = None
        self._status = None
        self._settings = None
        self._widgets = None
        self._wid_box = None

        if auto_start:
            self.initialize()
            # self.start()

    def display(self):
        if self._wid_box:
            IPython.display.display(self._wid_box)

    @property
    def mode(self):
        return self._mode

    def _update_mode(self, value):
        valid_modes = ['photo', 'video']

        value = status.current_mode(value)

        if value not in valid_modes:
            raise ValueError('Unexpected mode value: {}'.format(value))

        if value != self._mode:
            self._mode = value
            self.regenerate_widgets()
            self.update_widgets()

    def initialize(self):
        """Start everything in motion.  Call this in the beginning.
        """
        self.close()
        self.update_information()
        # self.initialize_widgets()
        self.display()
        # self.update_widgets()

    def regenerate_widgets(self):
        """Generate and display a set of dropdown widgets to control current mode options
        """
        self.close_children()

        self._widgets = Struct()
        for name, fid in api._feature_id[self.mode].items():
            self._widgets[name] = feature_dropdown_widget(self.mode, fid, name=name,
                                                          callback=self.update)

        # Place control widgets in a vertical layout box
        if not self._wid_box:
            self._wid_box = ipywidgets.VBox()

        self._wid_box.children = [w for w in self._widgets.values()]

    def update(self):
        self.update_information()
        self.update_widgets()

    def update_widgets(self):
        """Update displayed widgets with current camera settings
        """
        for name, wid in self._widgets.items():
            fid = api.feature_name_id(self.mode, name)
            value = self._settings[str(fid)]
            wid.value = value

    def update_information(self):
        """Update internal state with information retrieved from camera
        """
        raw_status, raw_settings = commands.get_raw_status_settings()
        # self._status = raw_status
        self._settings = raw_settings

        self._update_mode(raw_status)
        # self._update_mode(status.current_mode(raw_status))

    def close_children(self):
        """Close only child widgets inside container box.
        """
        if self._widgets:
            for wid in self._widgets.values():
                wid.close()
            self._widgets = None

        if self._wid_box:
            self._wid_box.children = []

    def close(self):
        """Close and remove all widgets.
        """
        self.close_children()

        if self._wid_box:
            self._wid_box.close()
            self._wid_box = None

    # #-------------------------------------------------
    # def task(self):
    #     """Work task to run in background thread
    #     """
    #     delta = 0.1
    #     while self._flag_run:
    #         info = status.fetch_camera_info()
    #         # text = self.status
    #         text = '<br>'.join(self.status.split('\n'))
    #         self.widget.value = _html_template.format(content=text)
    #         time_0 = time.time()
    #         while self._flag_run and time.time() - time_0 < self.interval:
    #             time.sleep(delta)
    #     self.widget.close()
    # def start(self):
    #     self.widget = ipywidgets.HTML()
    #     # self.widget.layout.width = '250pt'
    #     # self.widget.layout.height = '370pt'
    #     self.widget.layout.border = '1px solid grey'
    #     IPython.display.display(self.widget)
    #     self._flag_run = True
    #     self._thread = threading.Thread(target=self.task)
    #     self._thread.setDaemon(True)  # background thread is killed automaticalled when main thread exits.
    #     self._thread.start()
    # def stop(self):
    #     self._flag_run = False
    #     self._thread.join()
    # @property
    # def running(self):
    #     if self._thread:
    #         return self._thread.is_alive()
    #     else:
    #         return False

#------------------------------------------------

if __name__ == '__main__':
    pass

