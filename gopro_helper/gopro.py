
import time
import threading

import ipywidgets
import IPython

from . import status
from .api import get



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

        results = []
        results.append(time.ctime())

        sections = ['Setup', 'Photo', 'Video', 'System']
        for s in sections:
            if s in new_status:
                v = new_status[s]

                text = '{}:'.format(s)
                results.append(text)

                for x,y in v.items():
                    text = '    {:25s}: {}'.format(x,y)
                    results.append(text)

        self._status = '\n'.join(results)

    def task(self):
        delta = 0.1
        while self.flag_run:
            self.status = status.fetch_camera_info(pretty=True)
            self.widget.value = self.status

            time_0 = time.time()
            while self.flag_run and time.time() - time_0 < self.interval:
                time.sleep(delta)

        self.widget.close()

    def start(self):
        self.widget = ipywidgets.Textarea(font_family='monospace')
        self.widget.layout.width = '400pt'
        self.widget.layout.height = '500pt'
        self.widget.layout.border = '1px solid grey'
        self.widget.layout.font_family = 'DejaVu Sans Mono, Consolas, Lucida Console, Monospace'

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
