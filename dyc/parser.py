"""
This file is used to read the 
`dyc.yaml` configurations at the root of a project.

It parses all the configs to be consumed in DYC.
"""
import copy
import click
from .configs import Config


class ParsedConfig(Config):
    def __init__(self):
        self.plain = copy.deepcopy(self.default)
        try:
            self.override()
            self.config_err = False
        except AttributeError:
            self.config_err = True
