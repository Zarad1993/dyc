"""
Entry point to DYC Class

DYC (Document Your Code) Class initiator
is constructed here. It performs all the readings

"""
import click
from .utils import get_extension
from .methods import MethodBuilder
from .top import TopBuilder
from .classes import ClassBuilder
from .base import Processor


class DYC(Processor):
    def __init__(self, config, details=None, placeholders=False, skip_confirm=False):
        self.config = config
        self.placeholders = placeholders
        self.skip_confirm = skip_confirm

    def process_methods(self, diff_only=False, changes=[]):
        """
        Main method that documents methods in a file. To any
        file that needs to be documented. Process methods is the
        entry point for getting the whole thing done
        Parameters
        ----------
        bool diff_only: Use a diff only. Consumed by dyc diff.
        list changes: Changes in a file, mainly use also with dyc diff.
        """
        print("\nProcessing Methods\n\r")
        for filename in self.file_list:

            try:
                change = list(filter(lambda x: x.get("path") == filename, changes))[0]
            except TypeError as e:
                click.echo(
                    click.style("Error %r: USING default settings" % e, fg="red")
                )
                return
            except IndexError:
                change = None

            extension = get_extension(filename)
            fmt = self.formats.get(extension)
            method_cnf = fmt.get("method", {})
            method_cnf["arguments"] = fmt.get("arguments")
            builder = MethodBuilder(
                filename,
                method_cnf,
                placeholders=self.placeholders,
                skip_confirm=self.skip_confirm,
            )
            builder.initialize(change=change)
            builder.prompts()
            builder.apply()
            builder.clear(filename)

    def process_classes(self):
        """
        Main method that documents Classes in a file.
        """
        print("\nProcessing Classes\n\r")
        for filename in self.file_list:
            extension = get_extension(filename)
            fmt = self.formats.get(extension)
            classes_cnf = fmt.get("class", {})
            classes_cnf["parents"] = fmt.get("parents")
            builder = ClassBuilder(
                filename,
                classes_cnf,
                placeholders=self.placeholders,
                skip_confirm=self.skip_confirm,
            )
            builder.initialize()
            builder.prompts()
            builder.apply()
            builder.clear(filename)

    def process_top(self, diff_only=False):
        """
        Main method that documents a top of a file.
        """
        print("\nProcessing Top\n\r")
        for filename in self.file_list:

            extension = get_extension(filename)
            fmt = self.formats.get(extension)
            top_cnf = fmt.get("top", {})
            builder = TopBuilder(
                filename,
                top_cnf,
                placeholders=self.placeholders,
                skip_confirm=self.skip_confirm,
            )
            builder.prompts()
            builder.apply()
            builder.clear(filename)
