"""
This file contains all the event classes used in dyc. It contains
a Watcher that watches files for changes and a WatchEvent that
triggers if a file is changed.
"""
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from .diff import Diff
from .main import DYC


class WatchEvent(LoggingEventHandler):

    config = None

    def dispatch(self, event):
        """
        Temporary dispatch method as a POC for logger.
        Needs cleanup
        Parameters
        ----------
        FileModifiedEvent event: watchdog file of a modified event
        """
        diff = Diff(self.config.plain)
        uncommitted = diff.uncommitted
        paths = [
            idx.get('path')
            for idx in uncommitted
            if './{}'.format(idx.get('path')) == event.src_path
        ]
        filtered = [
            idx
            for idx in uncommitted
            if './{}'.format(idx.get('path')) == event.src_path
        ]
        if len(filtered):
            dyc = DYC(self.config.plain, placeholders=True)
            dyc.prepare(files=paths)
            dyc.process_methods(diff_only=True, changes=uncommitted)


class Watcher:
    @classmethod
    def start(cls, config):
        """
        The starter method for watching files.
        If invoked, it will start watching all files and see if documentation is needed

        Parameters
        ----------
        ConfigParser config: Config going to be used in DYC
        """
        logging.basicConfig(level=logging.INFO)
        observer = Observer()
        event_handler = WatchEvent()
        event_handler.config = config
        observer.schedule(event_handler, '.', recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print('Quitting..')
        observer.join()
