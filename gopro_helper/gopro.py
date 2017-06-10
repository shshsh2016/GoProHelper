
import time
import threading
from collections import OrderedDict

import ipywidgets
import IPython

from . import api
from . import status
from . import commands
from .network import get
from .namespace import Struct


_html_template = """
<p style="font-family:  DejaVu Sans Mono, Consolas, Lucida Console, Monospace;'
          font-variant: normal;
          font-weight:  normal;
          font-style:   normal;
          font-size:    12pt; ">
    <code style=display:block>
        {content:}
    </code>
</p>
"""
    # <code style=display:block;white-space:pre-wrap>


class GoProStatus():
    def __init__(self, auto_start=True, interval=10):
        self.flag_run = False
        self.interval = interval
        self._status = ''
        self._thread = None

        if auto_start:
            self.start()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, new_status):
        if not new_status:
            self._status = 'None'
            return

        results = ['']
        # results.append(time.ctime())

        # sections = ['Setup', 'Photo', 'Video', 'System']
        sections = ['photo', 'video', 'system']
        for s in sections:
            if s in new_status:
                v = new_status[s]

                text = '{}:'.format(s)
                results.append(text)

                for x,y in v.items():
                    text = '   {:11s}:  {}'.format(x,y)
                    results.append(text)

        self._status = '\n'.join(results)

    def task(self):
        """Work task to run in background thread
        """
        delta = 0.1
        while self.flag_run:
            self.status = status.fetch_camera_info(pretty=False)

            # text = self.status
            text = '<br>'.join(self.status.split('\n'))
            self.widget.value = _html_template.format(content=text)

            time_0 = time.time()
            while self.flag_run and time.time() - time_0 < self.interval:
                time.sleep(delta)

        self.widget.close()


    def start(self):
        self.widget = ipywidgets.HTML()
        # self.widget.layout.width = '250pt'
        # self.widget.layout.height = '370pt'
        self.widget.layout.border = '1px solid grey'

        IPython.display.display(self.widget)

        self.flag_run = True

        self._thread = threading.Thread(target=self.task)
        self._thread.setDaemon(True)  # background thread is killed automaticalled when main thread exits.
        self._thread.start()

    def stop(self):
        self.flag_run = False
        self._thread.join()

    @property
    def running(self):
        if self._thread:
            return self._thread.is_alive()
        else:
            return False



#################################################
#################################################
#################################################


def feature_dropdown_widget(mode, fid, name=None, value_init=0, width='200pt'):
    """Construct a dropdown widget for specified feature options.
    Attach event handler to send new values to camera.
    """
    _name, options = api.feature_choices(mode, fid)

    if not name:
        name = _name

    # Instantiate new dropdown widget
    wid = ipywidgets.Dropdown(value=value_init, options=options, description=name)
    wid.layout.width = width

    # Define event handler
    def handle_selection(event):
        value = event.new
        if value > -1:
            print('set {} {}'.format(fid, value))
            resp = commands.set_feature_value(fid, value)
            print(resp.status_code)

    # Attach event handler to widget
    wid.observe(handle_selection, names='value')

    return wid



class GoProSettings():
    def __init__(self, auto_start=True, interval=1):
        self.interval = interval
        self._thread = None
        self.flag_run = False
        self._mode = None
        self._wid_box = None
        self._widgets = None

        if auto_start:
            self.initialize()
            self.start()

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        if not isinstance(value, str):
            raise ValueError('Invalid mode value: '.format(value))
        self._mode = value.lower()

    def initialize(self):
        """Generate and display a set of dropdown widgets to control current mode options
        """
        info = status.fetch_camera_info()
        self.mode = info.mode

        self._widgets = Struct()
        for name, fid in api._feature_id[self.mode].items():
            self._widgets[name] = feature_dropdown_widget(mode, fid, name)

        # Place control widgets in a vertical layout box
        self._wid_box = ipywidgets.VBox( [w for w in self._widgets.values()] )
        IPython.display.display(self._wid_box)

    def update(self):
        """Update displayed widgets with current camera settings
        """
        status, settings = commands.get_status_settings()

        if self.mode == info.mode:
            # Update self
            info[info.mode]

            # value_init = feature_current_value(fid)
        else:
            # Reconfigure to new mode
            self.close()
            self.initialize()

    def close(self):
        if self._wid_box:
            self._wid_box.close()

    def task(self):
        """Work task to run in background thread
        """
        delta = 0.1
        while self.flag_run:
            info = status.fetch_camera_info(pretty=False)

            # text = self.status
            text = '<br>'.join(self.status.split('\n'))
            self.widget.value = _html_template.format(content=text)

            time_0 = time.time()
            while self.flag_run and time.time() - time_0 < self.interval:
                time.sleep(delta)

        self.widget.close()


    def start(self):
        self.widget = ipywidgets.HTML()
        # self.widget.layout.width = '250pt'
        # self.widget.layout.height = '370pt'
        self.widget.layout.border = '1px solid grey'

        IPython.display.display(self.widget)

        self.flag_run = True

        self._thread = threading.Thread(target=self.task)
        self._thread.setDaemon(True)  # background thread is killed automaticalled when main thread exits.
        self._thread.start()

    def stop(self):
        self.flag_run = False
        self._thread.join()

    @property
    def running(self):
        if self._thread:
            return self._thread.is_alive()
        else:
            return False

#------------------------------------------------

if __name__ == '__main__':
    pass

