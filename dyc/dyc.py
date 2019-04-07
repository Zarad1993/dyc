import click
from .parser import ParsedConfig
from .main import DYC
from diff import Diff
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

config = click.make_pass_decorator(ParsedConfig, ensure=True)
# ParsedConfig class wrapping all settings, on every Click command,
# passed as decorator
# Will pass the config as a first argument (Based on the order it is passed)


@click.group()
@config
def main(config):
    """
    The entering method to the CLI
    Parameters
    ----------
    ConfigParser config: Config going to be used in DYC
    """
    pass


@main.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=False)
@config
def start(config, files):
    """
    This is the entry point of starting DYC for the whole project.
    When you run `dyc start`. ParsedConfig will wrap all the
    files list going to loop
    over and add missing documentation on.
    """
    if files:
        config.plain['file_list'] = list(files)
    dyc = DYC(config.plain)
    dyc.prepare()
    dyc.process_methods()



@main.command()
@click.option('--watch', help='Add default placeholder when watching', is_flag=True, default=False)
@config
def diff(config, watch):
    """
    This argument will run DYC on DIFF patch only
    """
    class Event(LoggingEventHandler):
        def dispatch(self, event):
            """
            Temporary dispatch method as a POC for logger.
            Needs cleanup
            Parameters
            ----------
            FileModifiedEvent event: watchdog file of a modified event
            """
            diff = Diff(config.plain)
            uncommitted = diff.uncommitted
            paths = [idx.get('path') for idx in uncommitted if './{}'.format(idx.get('path')) == event.src_path]
            filtered = [idx for idx in uncommitted if './{}'.format(idx.get('path')) == event.src_path]
            if len(filtered):
                dyc = DYC(config.plain, placeholders=True)
                dyc.prepare(files=paths)
                dyc.process_methods(diff_only=True, changes=uncommitted)

    if watch:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        observer = Observer()
        event_handler = Event()
        observer.schedule(event_handler, '.', recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print('Quitting..')
        observer.join()
    else:
        diff = Diff(config.plain)
        uncommitted = diff.uncommitted
        paths = [idx.get('path') for idx in uncommitted]
        if len(uncommitted):
            dyc = DYC(config.plain)
            dyc.prepare(files=paths)
            dyc.process_methods(diff_only=True, changes=uncommitted)
