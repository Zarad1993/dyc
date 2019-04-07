import click
from .parser import ParsedConfig
from .main import DYC
from diff import Diff

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
@config
def diff(config):
    """
    This argument will run DYC on DIFF patch only
    """
    diff = Diff(config.plain)
    uncommitted = diff.uncommitted
    paths = [idx.get('path') for idx in uncommitted]
    if len(uncommitted):
        dyc = DYC(config.plain)
        dyc.prepare(files=paths)
        dyc.process_methods(diff_only=True, changes=uncommitted)
