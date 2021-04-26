"""
This file gets configuration from parser.ParsedConfig
and handles all the commands from the command line.
"""
import click
from .parser import ParsedConfig
from .main import DYC
from .diff import Diff
from .events import Watcher
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
@click.option("--placeholders", is_flag=True, default=False)
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=False)
@click.option("--skip-confirm", required=False, default=False, is_flag=True)
@config
def start(config, files, placeholders, skip_confirm):
    """
    This is the entry point of starting DYC for the whole project.
    When you run `dyc start`. ParsedConfig will wrap all the
    files list going to loop
    over and add missing documentation on.
    """
    if files:
        config.plain["file_list"] = list(files)
    dyc = DYC(config.plain, placeholders=placeholders, skip_confirm=skip_confirm)
    dyc.prepare()
    dyc.process_methods()
    dyc.process_top()
    dyc.process_classes()


@main.command()
@click.option(
    "--watch", help="Add default placeholder when watching", is_flag=True, default=False
)
@config
def diff(config, watch):
    """
    This argument will run DYC on DIFF patch only
    """
    if watch:
        Watcher.start(config)
    else:
        diff = Diff(config.plain)
        uncommitted = diff.uncommitted
        paths = [idx.get("path") for idx in uncommitted]
        if len(uncommitted):
            dyc = DYC(config.plain)
            dyc.prepare(files=paths)
            dyc.process_methods(diff_only=True, changes=uncommitted)
