
import time
import threading



class Task():
    """Base class for background work task
    """
    def __init__(self, interval=10, auto_start=False):
        self.interval = interval
        self._flag_run = False
        self._thread = None
        self.lock = threading.Lock()

        if auto_start:
            self.start()

    #--------------------------------------------

    def initialize(self):
        """Child classes need to override this method:
        - load config data from files
        - instantiate a widget
        - establish a network connection
        - etc
        """
        pass

    def update(self):
        """Child classes need to override this method to get their work done:
        - fetch new data
        - compute something
        - make some LEDs blink
        - etc
        """
        pass

    def finish(self):
        """This method is called automatically by the stop method as part of shutting down
        background thread.  Override this in order to do clean up work:
        - write data to files
        - close a widget
        - close a socket
        - etc
        """
        pass

    #--------------------------------------------

    @property
    def flag_run(self):
        with self.lock:
            return self._flag_run

    @flag_run.setter
    def flag_run(self, value):
        with self.lock:
            self._flag_run = value

    def _pause(self):
        delta = 0.01
        time_0 = time.time()
        while self.flag_run and time.time() - time_0 < self.interval:
            time.sleep(delta)

    def _work_task(self):
        """Manage work task lifecycle
        """
        with self.lock:
            self.initialize()

        while self.flag_run:
            with self.lock:
                self.update()

            self._pause()

        with self.lock:
            self.finish()

    def start(self):
        """Put everything in motion
        """
        if self.running:
            print('task already running...')
            return

        self.flag_run = True
        self._thread = threading.Thread(target=self._work_task)
        self._thread.setDaemon(True)  # True: this thread killed automaticalled when main thread exits.
        self._thread.start()

    @property
    def running(self):
        """Return True if background work thread is running
        """
        if self._thread:
            return self._thread.is_alive()
        else:
            return False

    def stop(self):
        """Terminate work task in background thread
        """
        if self.running:
            self.flag_run = False
            self._thread.join()
            self._thread = None
        else:
            print('nothing to stop, task is not running...')

#------------------------------------------------

if __name__ == '__main__':
    pass
